import os, logging, sys
import scipy.optimize, numpy, pylab, scipy.spatial.distance, scipy.stats
import shutil, h5py
import scipy.linalg, scipy.sparse

from circus.shared.files import load_data, write_datasets, get_overlaps, load_data_memshared, get_intersection_norm
from circus.shared.utils import get_tqdm_progressbar, get_shared_memory_flag, dip, dip_threshold, batch_folding_test_with_MPA, bhatta_dist, nd_bhatta_dist, test_if_support
from circus.shared.messages import print_and_log
from circus.shared.probes import get_nodes_and_edges
from circus.shared.mpi import all_gather_array, comm, gather_array, get_local_ring
import scipy.linalg, scipy.sparse
import statsmodels.api as sm

logger = logging.getLogger(__name__)


class DistanceMatrix(object):

    def __init__(self, size):
        self.size = size
        self.didx = lambda i,j: i*self.size + j - i*(i+1)//2 - i - 1

    def initialize(self, data, ydata=None):
        if ydata is None:
            self.distances = scipy.spatial.distance.pdist(data, 'euclidean').astype(numpy.float32)
        else:
            self.distances = scipy.spatial.distance.cdist(data, ydata, 'euclidean').astype(numpy.float32)

    def get_value(self, i, j):
        if i < j:
            return self.distances[self.didx(i, j)]
        elif i > j:
            return self.distances[self.didx(j, i)]
        elif i == j:
            return 0

    def get_row(self, i, with_diag=True):
        start = self.distances[self.didx(numpy.arange(0, i), i)]
        end = self.distances[self.didx(i, numpy.arange(i+1, self.size))]
        if with_diag:
            result = numpy.concatenate((start, numpy.array([0], dtype=numpy.float32), end))
        else:
            result = numpy.concatenate((start, end))
    
        return result

    def get_col(self, i, with_diag=True):
        return self.get_row(i, with_diag)

    def to_dense(self):
        return scipy.spatial.distance.squareform(self.distances)

    def get_rows(self, indices, with_diag=True):
        if with_diag:
            result = numpy.zeros((len(indices), self.size), dtype=numpy.float32)
        else:
            result = numpy.zeros((len(indices), self.size - 1), dtype=numpy.float32)

        for count, i in enumerate(indices):
            result[count] = self.get_row(i, with_diag)
        return result

    def get_cols(self, indices, with_diag=True):
        if with_diag:
            result = numpy.zeros((self.size, len(indices)), dtype=numpy.float32)
        else:
            result = numpy.zeros((self.size - 1, len(indices)), dtype=numpy.float32)

        for count, i in enumerate(indices):
            result[:, count] = self.get_col(i, with_diag)
        return result

    def get_deltas(self, rho):
        rho_sort_id = numpy.argsort(rho) # index to sort
        rho_sort_id = (rho_sort_id[::-1]) # reversing sorting indexes
        sort_rho = rho[rho_sort_id] # sortig rho in ascending order
        auxdelta = numpy.zeros(self.size, dtype=numpy.float32)

        for count, i in enumerate(rho_sort_id):
            line = self.get_row(i)[rho_sort_id[:count+1]]
            line[line == 0] = float("inf")
            auxdelta[count] = numpy.min(line)

        delta = numpy.zeros_like(auxdelta) 
        delta[rho_sort_id] = auxdelta 
        delta[rho == numpy.max(rho)] = numpy.max(delta[numpy.logical_not(numpy.isinf(delta))]) # assigns max delta to the max rho
        delta[numpy.isinf(delta)] = 0

        return numpy.nan_to_num(delta, copy=False)

    @property
    def max(self):
        return numpy.max(self.distances)

    def __del__(self):
        del self.distances
    

def fit_rho_delta(xdata, ydata, alpha=3):

    if xdata.min() == xdata.max():
        return numpy.zeros(0, dtype=numpy.int32)

    try:
        x = sm.add_constant(xdata)
        model = sm.RLM(ydata, x)
        results = model.fit()
        difference = ydata - results.fittedvalues
        factor = numpy.median(numpy.abs(difference - numpy.median(difference)))
        z_score = difference - alpha*factor*(1 + results.fittedvalues)
        centers = numpy.where(z_score >= 0)[0]
    except Exception:
        return numpy.zeros(0, dtype=numpy.int32)
    return centers

def compute_rho(data, update=None, mratio=0.01):
    N = len(data)
    nb_selec = max(5, int(mratio*N))
    rho = numpy.zeros(N, dtype=numpy.float32)
    dist_sorted = {}

    if update is None:
        dist = DistanceMatrix(N)
        dist.initialize(data)
        for i in range(N):
            data = dist.get_row(i, with_diag=False)
            if len(data) > nb_selec:
                dist_sorted[i] = data[numpy.argpartition(data, nb_selec)[:nb_selec]]
            else:
                dist_sorted[i] = data
            rho[i] = numpy.mean(dist_sorted[i])
        return numpy.nan_to_num(rho, copy=False), dist, dist_sorted
    else:
        for i in range(N):
            dist = scipy.spatial.distance.cdist(data[i].reshape(1, len(data[i])), update[0]).flatten()
            dist = numpy.concatenate((update[1][i], dist))
            if len(dist) > nb_selec:
                dist_sorted[i] = dist[numpy.argpartition(dist, nb_selec)[:nb_selec]]
            else:
                dist_sorted[i] = dist
            rho[i] = numpy.mean(dist_sorted[i])
        return numpy.nan_to_num(rho, copy=False), dist_sorted

def clustering_by_density(rho, dist, n_min, alpha=3):
    distances = DistanceMatrix(len(rho))
    distances.distances = dist
    delta = compute_delta(distances, rho)
    nclus, labels, centers = find_centroids_and_cluster(distances, rho, delta, alpha)
    halolabels = halo_assign(distances, labels, centers, n_min)
    halolabels -= 1
    centers = numpy.where(numpy.in1d(centers - 1, numpy.arange(halolabels.max() + 1)))[0]
    del distances
    return halolabels, rho, delta, centers

def compute_delta(dist, rho):
    return dist.get_deltas(rho)

def find_centroids_and_cluster(dist, rho, delta, alpha=3):

    npnts = len(rho)    
    centers = numpy.zeros(npnts)
    
    auxid = fit_rho_delta(rho, delta, alpha)
    nclus = len(auxid)

    centers[auxid] = numpy.arange(nclus) + 1 # assigning labels to centroids
    
    # assigning points to clusters based on their distance to the centroids
    if nclus <= 1:
        labels = numpy.ones(npnts)
    else:
        centersx = numpy.where(centers)[0] # index of centroids
        dist2cent = dist.get_rows(centersx)
        labels = numpy.argmin(dist2cent, axis=0) + 1
        _, cluscounts = numpy.unique(labels, return_counts=True) # number of elements of each cluster

    return nclus, labels, centers
    

def halo_assign(dist, labels, centers, n_min):

    halolabels = labels.copy()
    sameclusmat = numpy.equal(labels, labels[:, None]) #
    sameclus_cent = sameclusmat[centers > 0, :] # selects only centroids
    dist2cent = dist.get_rows(numpy.where(centers > 0)[0]) # distance to centroids
    dist2cluscent = dist2cent*sameclus_cent # preserves only distances to the corresponding cluster centroid
    nclusmem = numpy.sum(sameclus_cent, axis=1) # number of cluster members
    meandist2cent = numpy.sum(dist2cluscent, axis=1)/nclusmem # mean distance to corresponding centroid
    mad2cent = numpy.zeros(meandist2cent.shape)
    gt_meandist2cent = numpy.zeros(dist2cluscent.shape, dtype=numpy.bool)

    for i in range(len(meandist2cent)):
        idx = numpy.where(dist2cluscent[i] > 0)[0]
        mean_i = numpy.mean(dist2cluscent[i, idx])
        mad_i = numpy.median(numpy.abs(dist2cluscent[i, idx] - numpy.median(dist2cluscent[i, idx])))
        bound = mean_i + mad_i
        gt_meandist2cent[i] = dist2cluscent[i] > bound

        if numpy.sum(gt_meandist2cent[i]) - len(idx) < n_min:
            gt_meandist2cent[i] = False

    remids = numpy.sum(gt_meandist2cent, axis=0)
    halolabels[remids > 0] = 0 # setting to 0 the removes points

    return halolabels
    

def merging(groups, merging_method, merging_param, data):

    def perform_merging(groups, merging_method, merging_param, data):
        mask      = numpy.where(groups > -1)[0]
        clusters  = numpy.unique(groups[mask])
        dmin      = numpy.inf
        to_merge  = [None, None]

        for ic1 in range(len(clusters)):
            idx1 = numpy.where(groups == clusters[ic1])[0]
            sd1  = numpy.take(data, idx1, axis=0)

            if merging_method in ['distance', 'dip', 'folding', 'bhatta']:
                m1   = numpy.median(sd1, 0)
    
            for ic2 in range(ic1+1, len(clusters)):
                idx2 = numpy.where(groups == clusters[ic2])[0]
                sd2  = numpy.take(data, idx2, axis=0)
                
                if merging_method in ['distance', 'dip', 'folding', 'bhatta']:
                    m2   = numpy.median(sd2, 0)
                    v_n  = (m1 - m2)
                    pr_1 = numpy.dot(sd1, v_n)
                    pr_2 = numpy.dot(sd2, v_n)
                
                if merging_method == 'folding':
                    sub_data = numpy.concatenate([pr_1, pr_2])
                    unimodal, p_value, phi, _ = batch_folding_test_with_MPA(sub_data, True)
                    if unimodal:
                        dist = p_value
                    else:
                        dist = numpy.inf
                elif merging_method == 'nd-folding':
                    sub_data = numpy.vstack((sd1, sd2))[:, :3]
                    unimodal, p_value, phi, _ = batch_folding_test_with_MPA(sub_data, True)
                    if unimodal:
                        dist = p_value
                    else:
                        dist = numpy.inf
                elif merging_method == 'dip':
                    sub_data = numpy.concatenate([pr_1, pr_2])
                    if len(sub_data) > 5:
                        dist = dip(sub_data)/dip_threshold(len(sub_data), merging_param)
                    else:
                        dist = numpy.inf
                elif merging_method == 'distance':
                    med1 = numpy.median(pr_1)
                    med2 = numpy.median(pr_2)
                    mad1 = numpy.median(numpy.abs(pr_1 - med1))**2
                    mad2 = numpy.median(numpy.abs(pr_2 - med2))**2
                    norm = mad1 + mad2
                    dist = numpy.sqrt((med1 - med2)**2/norm)
                elif merging_method == 'bhatta':
                    try:
                        dist = bhatta_dist(pr_1, pr_2)
                    except Exception:
                        dist = numpy.inf
                elif merging_method == 'nd-bhatta':
                    try:
                        dist = nd_bhatta_dist(sd1.T, sd2.T)
                    except Exception:
                        dist = numpy.inf

                if dist < dmin:
                    dmin = dist
                    to_merge = [ic1, ic2]

        if merging_method == 'dip':
            thr = 1
        elif merging_method in ['folding', 'nd-folding', 'bhatta', 'nd-bhatta']:
            thr = merging_param
        elif merging_method == 'distance':
            thr = merging_param/0.674

        if dmin < thr:
            ic1, ic2 = to_merge
            c1, c2 = clusters[ic1], clusters[ic2]
            selection = numpy.where(groups == c2)[0]
            groups[selection] = c1
            merge = (c1, c2)
            return True, groups, merge, dmin

        return False, groups, None, None

    has_been_merged = True
    mask = numpy.where(groups > -1)[0]
    clusters = numpy.unique(groups[mask])
    merged = [len(clusters), 0]

    if merging_method == 'dip':
        thr = 1
    elif merging_method in ['folding', 'nd-folding', 'bhatta', 'nd-bhatta']:
        thr = merging_param
    elif merging_method == 'distance':
        thr = merging_param/0.674

    merge_history = {
        'merge': [],
        'distance': [],
        'method': merging_method,
        'threshold': thr,
    }

    while has_been_merged:
        has_been_merged, groups, merge, dmin = perform_merging(groups, merging_method, merging_param, data)
        if has_been_merged:
            merged[1] += 1
            merge_history['merge'].append(merge)
            merge_history['distance'].append(dmin)

    return groups, merged, merge_history


def slice_templates(params, to_remove=[], to_merge=[], extension='', input_extension=''):
    """Slice templates in HDF5 file.

    Arguments:
        params
        to_remove: list (optional)
            An array of template indices to remove.
            The default value is [].
        to_merge: list | numpy.ndarray (optional)
            An array of pair of template indices to merge
            (i.e. shape = (nb_merges, 2)).
            The default value is [].
        extension: string (optional)
            The extension to use as output.
            The default value is ''.
        input_extension: string (optional)
            The extension to use as input.
            The default value is ''.
    """

    file_out_suff  = params.get('data', 'file_out_suff')

    data_file      = params.data_file
    N_e            = params.getint('data', 'N_e')
    N_total        = params.nb_channels
    hdf5_compress  = params.getboolean('data', 'hdf5_compress')
    N_t            = params.getint('detection', 'N_t')
    template_shift = params.getint('detection', 'template_shift')
    has_support    = test_if_support(params, input_extension)

    if comm.rank == 0:
        print_and_log(['Node 0 is slicing templates'], 'debug', logger)
        old_templates  = load_data(params, 'templates', extension=input_extension)
        old_limits     = load_data(params, 'limits', extension=input_extension)
        if has_support:
            old_supports   = load_data(params, 'supports', extension=input_extension)
        _, N_tm        = old_templates.shape
        norm_templates = load_data(params, 'norm-templates', extension=input_extension)

        # Determine the template indices to delete.
        to_delete = list(to_remove)  # i.e. copy
        if to_merge != []:
            for count in range(len(to_merge)):
                remove = to_merge[count][1]
                to_delete += [remove]

        # Determine the indices to keep.
        all_templates = set(numpy.arange(N_tm // 2))
        to_keep = numpy.array(list(all_templates.difference(to_delete)))

        positions = numpy.arange(len(to_keep))


        # Initialize new HDF5 file for templates.
        local_keep = to_keep[positions]
        templates  = scipy.sparse.lil_matrix((N_e*N_t, 2*len(to_keep)), dtype=numpy.float32)
        hfilename  = file_out_suff + '.templates{}.hdf5'.format('-new')
        hfile      = h5py.File(hfilename, 'w', libver='earliest')
        norms      = hfile.create_dataset('norms', shape=(2*len(to_keep), ), dtype=numpy.float32, chunks=True)
        limits     = hfile.create_dataset('limits', shape=(len(to_keep), 2), dtype=numpy.float32, chunks=True)
        if has_support:
            supports   = hfile.create_dataset('supports', shape=(len(to_keep), N_e), dtype=numpy.bool, chunks=True)
        # For each index to keep.
        for count, keep in zip(positions, local_keep):
            # Copy template.
            templates[:, count]                = old_templates[:, keep]
            templates[:, count + len(to_keep)] = old_templates[:, keep + N_tm//2]
            # Copy norm.
            norms[count]                       = norm_templates[keep]
            norms[count + len(to_keep)]        = norm_templates[keep + N_tm//2]
            if has_support:
                supports[count]                = old_supports[keep]
            # Copy limits.
            if to_merge == []:
                new_limits = old_limits[keep]
            else:
                subset     = numpy.where(to_merge[:, 0] == keep)[0]
                if len(subset) > 0:
                    # pylab.subplot(211)
                    # pylab.plot(templates[:, count].toarray().flatten())
                    # ymin, ymax = pylab.ylim()
                    # pylab.subplot(212)
                    # for i in to_merge[subset]:
                    #     pylab.plot(old_templates[:, i[1]].toarray().flatten())
                    # pylab.ylim(ymin, ymax)
                    # pylab.savefig('merge_%d.png' %count)
                    # pylab.close()
                    # Index to keep is involved in merge(s) and limits need to
                    # be updated.
                    idx        = numpy.unique(to_merge[subset].flatten())
                    ratios     = norm_templates[idx] / norm_templates[keep]
                    new_limits = [
                        numpy.min(ratios * old_limits[idx][:, 0]),
                        numpy.max(ratios * old_limits[idx][:, 1])
                    ]
                else:
                    new_limits = old_limits[keep]
            limits[count]  = new_limits

        # Copy templates to file.
        templates = templates.tocoo()
        if hdf5_compress:
            hfile.create_dataset('temp_x', data=templates.row, compression='gzip')
            hfile.create_dataset('temp_y', data=templates.col, compression='gzip')
            hfile.create_dataset('temp_data', data=templates.data, compression='gzip')
        else:
            hfile.create_dataset('temp_x', data=templates.row)
            hfile.create_dataset('temp_y', data=templates.col)
            hfile.create_dataset('temp_data', data=templates.data)
        hfile.create_dataset('temp_shape', data=numpy.array([N_e, N_t, 2*len(to_keep)], dtype=numpy.int32))
        hfile.close()

        # Rename output filename.
        temporary_path = hfilename
        output_path = file_out_suff + '.templates{}.hdf5'.format(extension)
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(temporary_path, output_path)
    else:
        to_keep = numpy.array([])

    return to_keep


def slice_clusters(params, result, to_remove=[], to_merge=[], extension='',
    input_extension='', light=False, method='safe'):
    """Slice clusters in HDF5 templates.

    Arguments:
        params
        to_remove: list (optional)
        to_merge: list | numpy.ndarray (optional)
        extension: string (optional)
            The default value is ''.
        input_extension: string (optional)
            The default value is ''.
        light: boolean (optional)
    """

    file_out_suff  = params.get('data', 'file_out_suff')
    data_file      = params.data_file
    N_e            = params.getint('data', 'N_e')
    N_total        = params.nb_channels
    hdf5_compress  = params.getboolean('data', 'hdf5_compress')
    N_t            = params.getint('detection', 'N_t')
    template_shift = params.getint('detection', 'template_shift')

    if comm.rank == 0:

        print_and_log(['Node 0 is slicing clusters'], 'debug', logger)
        old_templates = load_data(params, 'templates', extension=input_extension)
        _, N_tm = old_templates.shape

        # Determine the template indices to delete.
        to_delete = list(to_remove)
        if to_merge != []:
            for count in range(len(to_merge)):
                remove     = to_merge[count][1]
                to_delete += [remove]

        # Determine the indices to keep.
        all_templates = set(numpy.arange(N_tm//2))
        to_keep = numpy.array(list(all_templates.difference(to_delete)))

        all_elements = [[] for i in range(N_e)]
        for target in numpy.unique(to_delete):
            elec     = result['electrodes'][target]
            nic      = target - numpy.where(result['electrodes'] == elec)[0][0]
            mask     = result['clusters_' + str(elec)] > -1
            tmp      = numpy.unique(result['clusters_' + str(elec)][mask])
            all_elements[elec] += list(numpy.where(result['clusters_' + str(elec)] == tmp[nic])[0])

        myfilename = file_out_suff + '.clusters{}.hdf5'.format(input_extension)
        myfile = h5py.File(myfilename, 'r', libver='earliest')

        for elec in range(N_e):
            if not light:
                result['data_' + str(elec)]     = numpy.delete(result['data_' + str(elec)], all_elements[elec], axis=0)
                result['clusters_' + str(elec)] = numpy.delete(result['clusters_' + str(elec)], all_elements[elec])
                result['times_' + str(elec)]    = numpy.delete(result['times_' + str(elec)], all_elements[elec])
                result['peaks_' + str(elec)]    = numpy.delete(result['peaks_' + str(elec)], all_elements[elec])
            else:
                result['clusters_' + str(elec)] = numpy.delete(result['clusters_' + str(elec)], all_elements[elec])
                data   = myfile.get('data_' + str(elec))[:]
                result['data_' + str(elec)]  = numpy.delete(data, all_elements[elec], axis=0)
                data   = myfile.get('times_' + str(elec))[:]
                result['times_' + str(elec)] = numpy.delete(data, all_elements[elec])
                data   = myfile.get('peaks_' + str(elec))[:]
                result['peaks_' + str(elec)] = numpy.delete(data, all_elements[elec])

        myfile.close()
        if method == 'safe':
            result['electrodes'] = numpy.delete(result['electrodes'], numpy.unique(to_delete))
        elif method == 'new':
            result['electrodes'] = result['electrodes'][to_keep]
        else:
            raise ValueError("Unexpected method value: {}".format(method))

        cfilename = file_out_suff + '.clusters{}.hdf5'.format('-new')
        cfile    = h5py.File(cfilename, 'w', libver='earliest')
        to_write = ['data_', 'clusters_', 'times_', 'peaks_']
        for ielec in range(N_e):
            write_datasets(cfile, to_write, result, ielec, compression=hdf5_compress)
        write_datasets(cfile, ['electrodes'], result)
        cfile.close()

        # Rename output file.
        temporary_path = cfilename
        output_path = file_out_suff + '.clusters{}.hdf5'.format(extension)
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(temporary_path, output_path)

    return


def slice_result(result, times):

    sub_results = []

    nb_temp = len(result['spiketimes'])
    for t in times:
        sub_result = {'spiketimes' : {}, 'amplitudes' : {}}
        for key in list(result['spiketimes'].keys()):
            spike_times = result['spiketimes'][key]
            spike_times = spike_times.ravel()
            amplitudes = result['amplitudes'][key]
            amplitudes = amplitudes.ravel()
            indices = numpy.where((spike_times >= t[0]) & (spike_times <= t[1]))[0]
            sub_result['spiketimes'][key] = spike_times[indices] - t[0]
            sub_result['amplitudes'][key] = amplitudes[indices]
        sub_results += [sub_result]

    return sub_results
    

def merging_cc(params, nb_cpu, nb_gpu, use_gpu):

    def remove(result, distances, cc_merge):
        do_merge  = True
        to_merge  = numpy.zeros((0, 2), dtype=numpy.int32)
        g_idx     = list(range(len(distances)))
        while do_merge:
            dmax      = distances.max()
            idx       = numpy.where(distances == dmax)
            one_merge = [idx[0][0], idx[1][0]]
            do_merge  = dmax >= cc_merge

            if do_merge:

                elec_ic1  = result['electrodes'][one_merge[0]]
                elec_ic2  = result['electrodes'][one_merge[1]]
                nic1      = one_merge[0] - numpy.where(result['electrodes'] == elec_ic1)[0][0]
                nic2      = one_merge[1] - numpy.where(result['electrodes'] == elec_ic2)[0][0]
                mask1     = result['clusters_' + str(elec_ic1)] > -1
                mask2     = result['clusters_' + str(elec_ic2)] > -1
                tmp1      = numpy.unique(result['clusters_' + str(elec_ic1)][mask1])
                tmp2      = numpy.unique(result['clusters_' + str(elec_ic2)][mask2])
                elements1 = numpy.where(result['clusters_' + str(elec_ic1)] == tmp1[nic1])[0]
                elements2 = numpy.where(result['clusters_' + str(elec_ic2)] == tmp2[nic2])[0]

                if len(elements1) > len(elements2):
                    to_remove = one_merge[1]
                    to_keep   = one_merge[0]
                    elec      = elec_ic2
                    elements  = elements2
                else:
                    to_remove = one_merge[0]
                    to_keep   = one_merge[1]
                    elec      = elec_ic1
                    elements  = elements1

                result['data_' + str(elec)]     = numpy.delete(result['data_' + str(elec)], elements, axis=0)
                result['clusters_' + str(elec)] = numpy.delete(result['clusters_' + str(elec)], elements)
                result['times_' + str(elec)]    = numpy.delete(result['times_' + str(elec)], elements)
                result['peaks_' + str(elec)]    = numpy.delete(result['peaks_' + str(elec)], elements)
                result['electrodes']            = numpy.delete(result['electrodes'], to_remove)
                distances                       = numpy.delete(distances, to_remove, axis=0)
                distances                       = numpy.delete(distances, to_remove, axis=1)
                to_merge                        = numpy.vstack((to_merge, numpy.array([g_idx[to_keep], g_idx[to_remove]])))
                g_idx.pop(to_remove)

        return to_merge, result

    data_file      = params.data_file
    N_e            = params.getint('data', 'N_e')
    N_total        = params.nb_channels
    N_t            = params.getint('detection', 'N_t')
    template_shift = params.getint('detection', 'template_shift')
    blosc_compress = params.getboolean('data', 'blosc_compress')

    N_tm           = load_data(params, 'nb_templates')
    nb_temp        = int(N_tm//2)
    to_merge       = []
    cc_merge       = params.getfloat('clustering', 'cc_merge')
    norm           = N_e * N_t
    decimation     = params.getboolean('clustering', 'decimation')

    if cc_merge < 1:

        result   = []
        overlap  = get_overlaps(params, extension='-merging', erase=True, normalize=True, maxoverlap=False, verbose=False, half=True, use_gpu=use_gpu, nb_cpu=nb_cpu, nb_gpu=nb_gpu, decimation=decimation)
        overlap.close()
        filename = params.get('data', 'file_out_suff') + '.overlap-merging.hdf5'

        SHARED_MEMORY = get_shared_memory_flag(params)

        if not SHARED_MEMORY:
            over_x, over_y, over_data, over_shape = load_data(params, 'overlaps-raw', extension='-merging')
        else:
            over_x, over_y, over_data, over_shape = load_data_memshared(params, 'overlaps-raw', extension='-merging', use_gpu=use_gpu, nb_cpu=nb_cpu, nb_gpu=nb_gpu)

        distances = numpy.zeros((nb_temp, nb_temp), dtype=numpy.float32)

        to_explore = numpy.arange(nb_temp - 1)[comm.rank::comm.size]

        for i in to_explore:

            idx = numpy.where((over_x >= i*nb_temp+i+1) & (over_x < ((i+1)*nb_temp)))[0]
            local_x = over_x[idx] - (i*nb_temp+i+1)
            data = numpy.zeros((nb_temp - (i + 1), over_shape[1]), dtype=numpy.float32)
            data[local_x, over_y[idx]] = over_data[idx]
            distances[i, i+1:] = numpy.max(data, 1)/norm
            distances[i+1:, i] = distances[i, i+1:]

        #Now we need to sync everything across nodes
        distances = gather_array(distances, comm, 0, 1, 'float32', compress=blosc_compress)
        if comm.rank == 0:
            distances = distances.reshape(comm.size, nb_temp, nb_temp)
            distances = numpy.sum(distances, 0)

        if comm.rank == 0:
            result = load_data(params, 'clusters')
            to_merge, result = remove(result, distances, cc_merge)

        to_merge = numpy.array(to_merge)
        to_merge = comm.bcast(to_merge, root=0)

        if len(to_merge) > 0:
            slice_templates(params, to_merge=to_merge)
            slice_clusters(params, result)

        comm.Barrier()

        del result, over_x, over_y, over_data

        if comm.rank == 0:
            os.remove(filename)

    return [nb_temp, len(to_merge)]


def delete_mixtures(params, nb_cpu, nb_gpu, use_gpu):

    data_file      = params.data_file
    N_e            = params.getint('data', 'N_e')
    N_total        = params.nb_channels
    N_t            = params.getint('detection', 'N_t')
    template_shift = params.getint('detection', 'template_shift')
    cc_merge       = params.getfloat('clustering', 'cc_merge')
    mixtures       = []
    to_remove      = []

    filename         = params.get('data', 'file_out_suff') + '.overlap-mixtures.hdf5'
    norm_templates   = load_data(params, 'norm-templates')
    best_elec        = load_data(params, 'electrodes')
    limits           = load_data(params, 'limits')
    nodes, edges     = get_nodes_and_edges(params)
    inv_nodes        = numpy.zeros(N_total, dtype=numpy.int32)
    inv_nodes[nodes] = numpy.arange(len(nodes))
    decimation       = params.getboolean('clustering', 'decimation')
    has_support      = test_if_support(params, '')

    overlap = get_overlaps(params, extension='-mixtures', erase=True, normalize=True, maxoverlap=False, verbose=False, half=True, use_gpu=use_gpu, nb_cpu=nb_cpu, nb_gpu=nb_gpu, decimation=decimation)
    overlap.close()

    SHARED_MEMORY = get_shared_memory_flag(params)

    if SHARED_MEMORY:
        c_overs    = load_data_memshared(params, 'overlaps', extension='-mixtures', use_gpu=use_gpu, nb_cpu=nb_cpu, nb_gpu=nb_gpu)
    else:
        c_overs    = load_data(params, 'overlaps', extension='-mixtures')

    if SHARED_MEMORY:
        templates  = load_data_memshared(params, 'templates', normalize=True)
    else:
        templates  = load_data(params, 'templates')

    x,        N_tm = templates.shape
    nb_temp        = int(N_tm//2)
    merged         = [nb_temp, 0]

    if has_support:
        supports = load_data(params, 'supports')
    else:
        supports = {}
        for t in range(N_e):
            elecs = numpy.take(inv_nodes, edges[nodes[t]])
            supports[t] = elecs

    overlap_0 = numpy.zeros(nb_temp, dtype=numpy.float32)
    distances = numpy.zeros((nb_temp, nb_temp), dtype=numpy.int32)

    for i in range(nb_temp-1):
        data = c_overs[i].toarray()
        distances[i, i+1:] = numpy.argmax(data[i+1:, :], 1)
        distances[i+1:, i] = distances[i, i+1:]
        overlap_0[i] = data[i, N_t - 1]

    all_temp    = numpy.arange(comm.rank, nb_temp, comm.size)
    sorted_temp = numpy.argsort(norm_templates[:nb_temp])[::-1]
    M           = numpy.zeros((2, 2), dtype=numpy.float32)
    V           = numpy.zeros((2, 1), dtype=numpy.float32)

    to_explore = range(comm.rank, nb_temp, comm.size)
    if comm.rank == 0:
        to_explore = get_tqdm_progressbar(to_explore)

    for count, k in enumerate(to_explore):

        k             = sorted_temp[k]
        overlap_k     = c_overs[k]
        if has_support:
            electrodes= numpy.where(supports[k])[0]
            all_idx   = [numpy.any(numpy.in1d(numpy.where(supports[t])[0], electrodes)) for t in range(nb_temp)]
        else:
            electrodes= numpy.take(inv_nodes, edges[nodes[best_elec[k]]])
            all_idx   = [numpy.any(numpy.in1d(supports[best_elec[t]], electrodes)) for t in range(nb_temp)]
        all_idx       = numpy.arange(nb_temp)[all_idx]
        been_found    = False
        t_k           = None

        for l, i in enumerate(all_idx):
            t_i = None
            if not been_found:
                overlap_i = c_overs[i]
                M[0, 0]   = overlap_0[i]
                V[0, 0]   = overlap_k[i, distances[k, i]]
                for j in all_idx[l+1:]:
                    t_j = None
                    M[1, 1]  = overlap_0[j]
                    M[1, 0]  = overlap_i[j, distances[k, i] - distances[k, j]]
                    M[0, 1]  = M[1, 0]
                    V[1, 0]  = overlap_k[j, distances[k, j]]
                    try:
                        [a1, a2] = numpy.dot(scipy.linalg.inv(M), V)
                    except Exception:
                        [a1, a2] = [0, 0]
                    a1_lim   = limits[i]
                    a2_lim   = limits[j]
                    is_a1    = (a1_lim[0] <= a1) and (a1 <= a1_lim[1])
                    is_a2    = (a2_lim[0] <= a2) and (a2 <= a2_lim[1])
                    if is_a1 and is_a2:
                        if t_k is None:
                            t_k = templates[:, k].toarray().ravel()
                        if t_i is None:
                            t_i = templates[:, i].toarray().ravel()
                        if t_j is None:
                            t_j = templates[:, j].toarray().ravel()
                        new_template = (a1*t_i + a2*t_j)
                        similarity   = numpy.corrcoef(t_k, new_template)[0, 1]
                        local_overlap = numpy.corrcoef(t_i, t_j)[0, 1]
                        if similarity > cc_merge and local_overlap < cc_merge:
                            if k not in mixtures:
                                mixtures  += [k]
                                been_found = True
                                break

    sys.stderr.flush()
    to_remove = numpy.unique(numpy.array(mixtures, dtype=numpy.int32))
    to_remove = all_gather_array(to_remove, comm, 0, dtype='int32')

    if len(to_remove) > 0 and comm.rank == 0:
        result = load_data(params, 'clusters')
        slice_templates(params, to_remove)
        slice_clusters(params, result, to_remove=to_remove)

    comm.Barrier()

    del c_overs

    if comm.rank == 0:
        os.remove(filename)

    return [nb_temp, len(to_remove)]