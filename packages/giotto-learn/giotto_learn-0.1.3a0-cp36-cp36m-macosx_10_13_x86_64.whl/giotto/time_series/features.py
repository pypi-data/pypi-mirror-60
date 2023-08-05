"""Features from time series."""
# License: Apache 2.0

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from joblib import Parallel, delayed, effective_n_jobs
from sklearn.utils import gen_even_slices
from sklearn.utils.validation import check_is_fitted, check_array

import warnings

warnings.warn(
    "Starting at v0.1.4, this package was renamed as 'giotto-tda'. The "
    "giotto-learn PyPI package will no longer be developed or maintained, and "
    "will remain at the state of v0.1.3. Please visit "
    "https://github.com/giotto-ai/giotto-tda to find installation information "
    "for giotto-tda.")


class PermutationEntropy(BaseEstimator, TransformerMixin):
    """Entropies from sets of permutations arg-sorting rows in arrays.

    Given a two-dimensional array `A`, another array `A'` of the same size is
    computed by arg-sorting each row in `A`. The permutation entropy [1]_ of
    `A` is the Shannon entropy of the probability distribution given by
    the relative frequencies of each arg-sorting permutation in `A'`.

    Parameters
    ----------
    n_jobs : int or None, optional, default: ``None``
        The number of jobs to use for the computation. ``None`` means 1 unless
        in a :obj:`joblib.parallel_backend` context. ``-1`` means using all
        processors.

    See also
    --------
    TakensEmbedding, giotto.diagrams.PersistenceEntropy

    References
    ----------
    .. [1] C. Bandt and B. Pompe, "Permutation Entropy: A Natural Complexity
           Measure for Time Series"; *Phys. Rev. Lett.*, **88**.17, 2002;
           `doi: 10.1103/physrevlett.88.174102
           <https://doi.org/10.1103/physrevlett.88.174102>`_.

    """

    def __init__(self, n_jobs=None):
        self.n_jobs = n_jobs

    def _entropy(self, X):
        Xo = np.unique(X, axis=0, return_counts=True)[1].reshape(-1, 1)
        Xo = Xo / np.sum(Xo, axis=0).reshape(-1, 1)
        return -np.sum(np.nan_to_num(Xo * np.log2(Xo)), axis=0).reshape(-1, 1)

    def _permutation_entropy(self, X):
        Xo = np.argsort(X, axis=2)
        Xo = np.stack([self._entropy(Xo[i]) for i in range(Xo.shape[0])])
        return Xo.reshape(-1, 1)

    def fit(self, X, y=None):
        """Do nothing and return the estimator unchanged.

        This method is there to implement the usual scikit-learn API and hence
        work in pipelines.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_points, n_dimensions)
            Input data.

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        self : object

        """
        check_array(X, allow_nd=True)

        self._is_fitted = True
        return self

    def transform(self, X, y=None):
        """Calculate the permutation entropy of each two-dimensional array in
        `X`.

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_points, n_dimensions)
            Input data.

        y : None
            There is no need for a target in a transformer, yet the pipeline
            API requires this parameter.

        Returns
        -------
        Xt : ndarray of int, shape (n_samples, 1)
            One permutation entropy per entry in `X` along axis 0.

        """

        # Check if fit had been called
        check_is_fitted(self, ['_is_fitted'])
        X = check_array(X, allow_nd=True)

        Xt = Parallel(n_jobs=self.n_jobs)(delayed(
            self._permutation_entropy)(X[s])
            for s in gen_even_slices(len(X), effective_n_jobs(self.n_jobs)))
        Xt = np.concatenate(Xt)
        return Xt
