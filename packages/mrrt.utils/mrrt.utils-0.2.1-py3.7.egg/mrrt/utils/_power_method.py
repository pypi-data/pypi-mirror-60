import numpy as np

from ._cupy import get_array_module


def power_method(
    A,
    dtype=None,
    xrand=None,
    niter=20,
    lam_diff_thresh=0.02,
    verbose=True,
    return_full=False,
    xp=None,
):
    """ power method for estimating the largest eigenvalue of A.

    Parameters
    ----------
    A : 2d array or mrrt.operators.LinearOperator
        The matrix on which to estimate the largest eigenvalue.
    dtype : array dtype, optional
        If specified, set the vector to have this dtype
        (default is complex128).
    niter : int, optional
        The maximum number of iterations to run
    errnorm_thresh : float, optional
        Stopping criterion (see code)
    verbose : bool, optional
        If True, print the estimate at each iteration.
    return_full : bool, optional
        If True, return the vector in addition to the eigenvalue.

    Returns
    -------
    lam : float
        Estimate of the largest eigenvalue of A.

    """
    if hasattr(A, "norm") and A.norm is not None:
        # check if operator has an optimized norm method
        use_norm_func = True
    else:
        use_norm_func = False

    if hasattr(A, "xp"):
        xp = A.xp
    else:
        xp, on_gpu = get_array_module(A, xp=xp)

    if not hasattr(A, "shape"):
        raise ValueError("A must have a shape attribute")
    if len(A.shape) != 2:
        raise ValueError("A must be 2D")
    if (not use_norm_func) and (A.shape[0] != A.shape[1]):
        raise ValueError("A must be a square matrix")

    if dtype is None and hasattr(A, "dtype"):
        dtype = A.dtype

    if xrand is None:
        xrand = xp.random.randn(A.shape[1])
        if xp.dtype(dtype).kind == "c":
            xrand = 1j * xp.random.randn(A.shape[1])
        xrand = xrand / xp.linalg.norm(xrand)
        if dtype is not None:
            xrand = xrand.astype(dtype)
    if isinstance(A, xp.ndarray):
        use_dot = True
    else:
        use_dot = False
    b = xrand.copy()
    b_prev = xp.squeeze(b)
    lam = lam_prev = np.Inf
    for n in range(niter):
        if use_dot:
            b = xp.dot(A, b)
        else:
            if use_norm_func:
                b = A.norm(b)
            else:
                b = A * b  # assumes a LinOp norm operator  (e.g. A = A1.H*A1)
        # b = Gn.H * (D * (Gn * b))
        b = xp.squeeze(b)

        if n > 0:
            lam_prev = lam

        # lam = xp.linalg.norm(b)
        # errnorm = xp.linalg.norm(bdiff)
        lam = xp.sqrt(xp.sum((xp.conj(b) * b).real))
        bdiff = b - b_prev
        errnorm = xp.sqrt(xp.sum((xp.conj(bdiff) * bdiff).real))

        if verbose:
            print("lam = {}, errnorm={}".format(lam, errnorm))
        b_prev = b.copy()
        b /= lam

        abs_lam_diff = xp.abs(lam_prev - lam) / lam
        if verbose and n > 0:
            print("abs_lam_diff = {}".format(abs_lam_diff))
        if lam_diff_thresh is not None and abs_lam_diff < lam_diff_thresh:
            print(
                "power_method reached convergence at iteration "
                "{}".format(n + 1)
            )
            break

    if return_full:
        return b, lam
    else:
        return lam
