import numpy as np
from scipy.sparse import coo_matrix

__all__ = ["hist_equal"]


def hist_equal(data=None, ncent=None, ifsame="orig", dmin=None, dmax=None):
    """Fast histogram of multidimensional data into equally-spaced bins.

    Parameters
    ----------
    data : ndarray
        The data to be binned. It should have shape(n, m) (m-dimensional).
    ncent : ndarray
        The number of centroids to use on each dimension.
    ifsame : {"orig", "1bin"}
        What to do if all data is the same along some dimension. "orig" means
        use the original ``ncent`` values. "1bin" means ignore ``ncent`` and
        use 1 bin
    dmin : tuple of float, optional
        TODO
    dmax : tuple of float, optional
        TODO

    Returns
    -------
    nk : ndarray
        The histogram values.
    center : list of ndarray
        List of bin centers for each dimension. ``len(center)`` will be equal
        to ``data.ndim``.

    Notes
    -----
    Matlab version by Jeff Fessler, The University of Michigan
    Python port by Gregory Lee
    """
    if ncent is None:
        raise ValueError("must specify # of centroids")

    data = np.asarray(data)
    if data.ndim == 1:
        data = data[:, np.newaxis]

    n, m = data.shape
    if m != len(ncent):
        raise ValueError("bad dimensions")

    slist = np.zeros((n, m))
    center = []
    if dmin is None:
        dmin = [np.min(data[:, d]) for d in range(m)]
    elif np.isscalar(dmin) or len(dmin) != m:
        raise ValueError("dmin must have length equal to data.shape[1]")
    if dmax is None:
        dmax = [np.max(data[:, d]) for d in range(m)]
    elif np.isscalar(dmax) or len(dmax) != m:
        raise ValueError("dmin must have length equal to data.shape[1]")
    for d, _dmin, _dmax in zip(range(m), dmin, dmax):
        nc = ncent[d]
        if _dmin == _dmax:
            if ifsame == "orig":
                center[d] = _dmin + np.arange(nc)
                slist[:, d] = 0
            elif ifsame == "1bin":
                ncent[d] = 1
                center[d] = _dmin
                slist[:, d] = 0
            else:
                raise ValueError('option ifsame="%s" unknown' % ifsame)
        else:
            fudge = 1.001
            _dmin = _dmin * fudge
            _dmax = _dmax / fudge
            center.append(np.linspace(_dmin, _dmax, nc))
            ddif = center[d][1] - center[d][0]
            ii = np.floor((data[:, d] - _dmin) / ddif)
            ii = np.clip(ii, 0, nc)
            slist[:, d] = ii

    s = np.cumprod(ncent)
    s = np.concatenate((np.array([1]), s[0:-1]), axis=0)

    slist = np.dot(slist, s)

    # sparse trick: much faster
    s = coo_matrix(
        (np.ones(n), (np.arange(n), slist)), shape=(n, np.prod(ncent))
    )
    nk = np.asarray(s.sum(axis=0))
    nk = nk.reshape(ncent, order="F")

    return (nk, center)
