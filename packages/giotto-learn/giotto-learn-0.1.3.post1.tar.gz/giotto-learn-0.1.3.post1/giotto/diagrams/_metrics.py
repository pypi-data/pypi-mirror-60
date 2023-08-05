# License: Apache 2.0

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform
from giotto_bottleneck import bottleneck_distance
from giotto_wasserstein import wasserstein_distance
from scipy.ndimage import gaussian_filter
from joblib import Parallel, delayed, effective_n_jobs
from sklearn.utils.validation import _num_samples
from sklearn.utils import gen_even_slices
from ._utils import _subdiagrams


def betti_curves(diagrams, sampling):
    born = sampling >= diagrams[:, :, 0]
    not_dead = sampling < diagrams[:, :, 1]
    alive = np.logical_and(born, not_dead)
    betti = np.sum(alive, axis=2).T
    return betti


def landscapes(diagrams, sampling, n_layers):
    n_points = diagrams.shape[1]

    midpoints = (diagrams[:, :, 1] + diagrams[:, :, 0]) / 2.
    heights = (diagrams[:, :, 1] - diagrams[:, :, 0]) / 2.
    fibers = np.maximum(-np.abs(sampling - midpoints) + heights, 0)
    top_pos = range(n_points - n_layers, n_points)
    fibers.partition(top_pos, axis=2)
    fibers = np.flip(fibers[:, :, -n_layers:], axis=2)
    fibers = np.transpose(fibers, (1, 2, 0))
    pad_with = ((0, 0), (0, max(0, n_layers - n_points)), (0, 0))
    fibers = np.pad(fibers, pad_with, 'constant', constant_values=0)
    return fibers


def _heat(heat, sampled_diag, sigma):
    unique, counts = np.unique(sampled_diag, axis=0, return_counts=True)
    unique = tuple(tuple(row) for row in unique.T)
    heat[unique] = counts
    heat[:, :] = gaussian_filter(heat, sigma, mode='reflect')


def heats(diagrams, sampling, step_size, sigma):
    heats_ = np.zeros((diagrams.shape[0], sampling.shape[0],
                       sampling.shape[0]))
    sampled_diags = np.copy(diagrams)
    sampling_ = sampling.reshape((-1,))
    sampled_diags[diagrams < sampling_[0]] = sampling_[0]
    sampled_diags[diagrams > sampling_[-1]] = sampling_[-1]
    sampled_diags = np.array((sampled_diags - sampling_[0]) / step_size,
                             dtype=int)
    [_heat(heats_[i], sampled_diag, sigma)
     for i, sampled_diag in enumerate(sampled_diags)]
    heats_ = heats_ - np.transpose(heats_, (0, 2, 1))
    heats_ = np.rot90(heats_, k=1, axes=(1, 2))
    return heats_


def betti_distances(diagrams_1, diagrams_2, sampling, step_size,
                    p=2., **kwargs):
    betti_curves_1 = betti_curves(diagrams_1, sampling)
    if np.array_equal(diagrams_1, diagrams_2):
        unnorm_dist = squareform(pdist(betti_curves_1, 'minkowski', p=p))
        return (step_size ** (1 / p)) * unnorm_dist
    betti_curves_2 = betti_curves(diagrams_2, sampling)
    unnorm_dist = cdist(betti_curves_1, betti_curves_2, 'minkowski', p=p)
    return (step_size ** (1 / p)) * unnorm_dist


def landscape_distances(diagrams_1, diagrams_2, sampling, step_size,
                        p=2., n_layers=1, **kwargs):
    n_samples_1, n_points_1 = diagrams_1.shape[:2]
    n_layers_1 = min(n_layers, n_points_1)
    if np.array_equal(diagrams_1, diagrams_2):
        ls_1 = landscapes(diagrams_1, sampling, n_layers_1).reshape(
            n_samples_1, -1)
        unnorm_dist = squareform(pdist(ls_1, 'minkowski', p=p))
        return (step_size ** (1 / p)) * unnorm_dist
    n_samples_2, n_points_2 = diagrams_2.shape[:2]
    n_layers_2 = min(n_layers, n_points_2)
    n_layers = max(n_layers_1, n_layers_2)
    ls_1 = landscapes(diagrams_1, sampling, n_layers).reshape(
        n_samples_1, -1)
    ls_2 = landscapes(diagrams_2, sampling, n_layers).reshape(
        n_samples_2, -1)
    unnorm_dist = cdist(ls_1, ls_2, 'minkowski', p=p)
    return (step_size ** (1 / p)) * unnorm_dist


def bottleneck_distances(diagrams_1, diagrams_2, delta=0.01, **kwargs):
    return np.array([[
        bottleneck_distance(
            diagram_1[diagram_1[:, 0] != diagram_1[:, 1]],
            diagram_2[diagram_2[:, 0] != diagram_2[:, 1]], delta)
        for diagram_2 in diagrams_2] for diagram_1 in diagrams_1])


def wasserstein_distances(diagrams_1, diagrams_2, p=2, delta=0.01,
                          **kwargs):
    return np.array([[
        wasserstein_distance(
            diagram_1[diagram_1[:, 0] != diagram_1[:, 1]],
            diagram_2[diagram_2[:, 0] != diagram_2[:, 1]], p, delta)
        for diagram_2 in diagrams_2] for diagram_1 in diagrams_1])


def heat_distances(diagrams_1, diagrams_2, sampling, step_size,
                   sigma=1., p=2., **kwargs):
    heat_1 = heats(diagrams_1, sampling, step_size, sigma).\
        reshape(diagrams_1.shape[0], -1)
    if np.array_equal(diagrams_1, diagrams_2):
        unnorm_dist = squareform(pdist(heat_1, 'minkowski', p=p))
        return (step_size ** (1 / p)) * unnorm_dist
    heat_2 = heats(diagrams_2, sampling, step_size, sigma).\
        reshape(diagrams_2.shape[0], -1)
    unnorm_dist = cdist(heat_1, heat_2, 'minkowski', p=p)
    return (step_size ** (1 / p)) * unnorm_dist


implemented_metric_recipes = {'bottleneck': bottleneck_distances,
                              'wasserstein': wasserstein_distances,
                              'landscape': landscape_distances,
                              'betti': betti_distances,
                              'heat': heat_distances}


def _matrix_wrapper(distance_func, distance_matrices, slice_, dim,
                    *args, **kwargs):
    distance_matrices[:, slice_, int(dim)] = distance_func(*args, **kwargs)


def _parallel_pairwise(X1, X2, metric, metric_params,
                       homology_dimensions, n_jobs):
    metric_func = implemented_metric_recipes[metric]
    effective_metric_params = metric_params.copy()
    none_dict = {dim: None for dim in homology_dimensions}
    samplings = effective_metric_params.pop('samplings', none_dict)
    step_sizes = effective_metric_params.pop('step_sizes', none_dict)

    if X2 is None:
        X2 = X1

    distance_matrices = Parallel(n_jobs=n_jobs)(delayed(metric_func)(
        _subdiagrams(X1, [dim], remove_dim=True),
        _subdiagrams(X2[s], [dim], remove_dim=True),
        sampling=samplings[dim], step_size=step_sizes[dim],
        **effective_metric_params) for dim in homology_dimensions
        for s in gen_even_slices(X2.shape[0], effective_n_jobs(n_jobs)))

    distance_matrices = np.concatenate(distance_matrices, axis=1)
    distance_matrices = np.stack(
        [distance_matrices[:, i*X2.shape[0]: (i+1)*X2.shape[0]]
         for i in range(len(homology_dimensions))], axis=2)
    return distance_matrices


def betti_amplitudes(diagrams, sampling, step_size, p=2., **kwargs):
    bcs = betti_curves(diagrams, sampling)
    return (step_size ** (1 / p)) * np.linalg.norm(bcs, axis=1, ord=p)


def landscape_amplitudes(diagrams, sampling, step_size, p=2., n_layers=1,
                         **kwargs):
    ls = landscapes(diagrams, sampling, n_layers).reshape(len(diagrams), -1)
    return (step_size ** (1 / p)) * np.linalg.norm(ls, axis=1, ord=p)


def bottleneck_amplitudes(diagrams, **kwargs):
    dists_to_diago = np.sqrt(2) / 2. * (diagrams[:, :, 1] - diagrams[:, :, 0])
    return np.linalg.norm(dists_to_diago, axis=1, ord=np.inf)


def wasserstein_amplitudes(diagrams, p=2., **kwargs):
    dists_to_diago = np.sqrt(2) / 2. * (diagrams[:, :, 1] - diagrams[:, :, 0])
    return np.linalg.norm(dists_to_diago, axis=1, ord=p)


def heat_amplitudes(diagrams, sampling, step_size, sigma=1., p=2.,
                    **kwargs):
    heat = heats(diagrams, sampling, step_size, sigma)
    return np.linalg.norm(heat, axis=(1, 2), ord=p)


implemented_amplitude_recipes = {'bottleneck': bottleneck_amplitudes,
                                 'wasserstein': wasserstein_amplitudes,
                                 'landscape': landscape_amplitudes,
                                 'betti': betti_amplitudes,
                                 'heat': heat_amplitudes}


def _arrays_wrapper(amplitude_func, amplitude_arrays, slice_, dim,
                    *args, **kwargs):
    amplitude_arrays[slice_, int(dim)] = amplitude_func(*args, **kwargs)


def _parallel_amplitude(X, metric, metric_params, homology_dimensions, n_jobs):
    amplitude_func = implemented_amplitude_recipes[metric]
    effective_metric_params = metric_params.copy()
    none_dict = {dim: None for dim in homology_dimensions}
    samplings = effective_metric_params.pop('samplings', none_dict)
    step_sizes = effective_metric_params.pop('step_sizes', none_dict)

    amplitude_arrays = Parallel(n_jobs=n_jobs)(delayed(amplitude_func)(
        _subdiagrams(X, [dim], remove_dim=True)[s], sampling=samplings[dim],
        step_size=step_sizes[dim], **effective_metric_params)
        for dim in homology_dimensions
        for s in gen_even_slices(_num_samples(X), effective_n_jobs(n_jobs)))

    amplitude_arrays = np.concatenate(amplitude_arrays).reshape(
        len(homology_dimensions), X.shape[0]).T

    return amplitude_arrays
