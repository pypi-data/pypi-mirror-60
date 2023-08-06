import functools
from operator import mul
import warnings

import numpy as np
from scipy.special import jv

from ._cupy import get_array_module


__all__ = [
    "complexify",
    "define_if",
    "jinc",
    "max_percent_diff",
    "nullcontext",
    "outer_sum",
    "pinv_tol",
    "prod",
    "profile",
    "reale",
    "rect",
    "rss",
]


"""
@profile decorator that does nothing when line profiler is not active

see:
http://stackoverflow.com/questions/18229628/python-profiling-using-line-profiler-clever-way-to-remove-profile-statements

"""
try:
    import builtins

    profile = builtins.__dict__["profile"]
except (AttributeError, KeyError):
    # No line profiler, provide a pass-through version
    def profile(func):
        return func


def define_if(condition, errmsg="requested function not available"):
    """Decorator for conditional definition of a function.

    Parameters
    ----------
    condition : bool
        If True the function is called normally.  If False, a
        ``NotImplementedError`` is raised when the function is called.
    errmsg: str, optional
        The error message to print when ``condition`` is False.

    Returns
    -------
    func : function wrapper
    """

    def decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            if condition:
                return func(*args, **kwargs)
            else:
                raise NotImplementedError(errmsg)

        return func_wrapper

    return decorator


def rect(x, xp=None):
    """Unit-width rect function

    This signal is nonzero where ``np.abs(x) < 0.5``.
    """
    xp, on_gpu = get_array_module(x, xp=xp)
    x = xp.atleast_1d(x)
    y = xp.abs(x) < 0.5
    return y


def jinc(x, xp=None):
    """Jinc function.

    Notes
    -----
    jinc(x) = J_1(pi x) / (2 x), where J_1 is Bessel function of the first
    kind of order 1.

    This is the 2D Fourier transform of a disk of diameter 1, so its DC value
    is the area of that disk which is ``np.pi / 4``.
    """
    xp, on_gpu = get_array_module(x, xp)
    if on_gpu:
        # jv not available in CuPy, so have to transfer to/from numpy
        x = np.atleast_1d(x.get())
    else:
        x = np.atleast_1d(x)
    # kludge for bessel with negative arguments, perhaps not needed
    x = np.abs(x)
    y = np.pi / 4 + np.zeros_like(x)  # jinc(0) = pi/4
    ig = x != 0
    y[ig] = jv(1, np.pi * x[ig]) / (2 * x[ig])
    if on_gpu:
        y = xp.asarray(y)
    return y


def reale(x, com="error", tol=None, msg=None, xp=None):
    """Return real part of complex data (with error checking).

    Parameters
    ----------
    x : array-like
        The data to check.
    com : {'warn', 'error', 'display', 'report'}
        Control rather to raise a warning, an error, or to just display to the
        console.  If ``com == 'report'``, the relative magnitude of the
        imaginary component is printed to the console.
    tol : float or None
        Allow complex values below ``tol`` in magnitude.  If None, ``tol`` will
        be ``1000*eps``.
    msg : str or None
        Additional message to print upon encountering complex values.

    Notes
    -----
    Based on Jeff Fessler's Matlab function of the same name.
    Python port by Gregory Lee.
    """
    xp, on_gpu = get_array_module(x, xp)
    if not xp.iscomplexobj(x):
        return x

    if tol is None:
        tol = 1000 * xp.finfo(x.dtype).eps

    if com not in ["warn", "error", "display", "report"]:
        raise ValueError(
            (
                "Bad com: {}.  It must be one of {'warn', 'error', 'display', "
                "'report'}"
            ).format(com)
        )

    max_abs_x = xp.max(xp.abs(x))
    if max_abs_x == 0:
        if xp.any(xp.abs(xp.imag(x)) > 0):
            raise RuntimeError("max real 0, but imaginary!")
        else:
            return xp.real(x)

    frac = xp.max(xp.abs(x.imag)) / max_abs_x
    if com == "report":
        print("imaginary part %g%%" % frac * 100)

    if frac > tol:
        t = "imaginary fraction of x is %g (tol=%g)" % (frac, tol)
        if msg is not None:
            t += "\n" + msg
        if com == "display":
            print(t)
        elif com == "warn":
            warnings.warn(t)
        else:
            raise RuntimeError(t)

    return xp.real(x)


def complexify(x, complex_dtype=None, xp=None):
    """Promote to complex if real input was provided.

    Parameters
    ----------
    x : array-like
        The array to convert
    complex_dtype : np.complex64, np.complex128 or None
        The dtype to use.  If None, the dtype used will be the one returned by
        ``np.result_tupe(x.dtype, np.complex64)``.

    Returns
    -------
    xc : array-like
        Complex-valued x.

    Notes
    -----
    Based on Jeff Fessler's Matlab function of the same name.
    Python port by Gregory Lee.
    """
    xp, on_gpu = get_array_module(x, xp)
    x = xp.asarray(x)

    if xp.iscomplexobj(x) and (x.dtype == complex_dtype):
        return x

    if complex_dtype is None:
        # determine complex datatype to use based on numpy's promotion rules
        complex_dtype = xp.result_type(x.dtype, xp.complex64)

    return xp.asarray(x, dtype=complex_dtype)


def max_percent_diff(s1, s2, use_both=False, doprint=False, xp=None):
    """Maximum percent difference between two signals.

    Parameters
    ----------
    s1, s2 : array-like
        The two signals to compare. These should have the same shape.
    use_both: bool, optional
        If True use the maximum across ``s1``, ``s2`` as the normalizer.
        Otherwise the maximum across ``s1`` is used.

    Returns
    -------
    d : float
        The maximum percent difference (in range [0, 100]).

    Notes
    -----
    Based on Jeff Fessler's Matlab function of the same name.
    Python port by Gregory Lee.
    """
    xp, on_gpu = get_array_module(s1, xp=xp)
    s1 = xp.squeeze(xp.asarray(s1))
    s2 = xp.squeeze(xp.asarray(s2))

    # first check that we have comparable signals!
    if s1.shape != s2.shape:
        raise ValueError("size mismatch")

    if xp.any(xp.isnan(s1)) | xp.any(xp.isnan(s2)):
        raise ValueError("NaN values found in input")

    if use_both:
        max1 = xp.abs(s1).max()
        max2 = xp.abs(s2).max()
        try:
            # transfer from GPU
            max1.get()
            max2.get()
        except AttributeError:
            pass
        denom = max(max1, max2)
        if denom == 0:
            return 0
    else:
        denom = xp.abs(s1).max()
        if denom == 0:
            denom = xp.abs(s2).max()
        if denom == 0:
            return 0
    d = xp.max(xp.abs(s1 - s2)) / denom
    return d * 100


def pinv_tol(x, tol=None, xp=None):
    """pinv with tolerance based on frobenious norm.

    Parameters
    ----------
    x : ndarray
        The matrix to invert.
    tol : {None, float, "fro", 2-tuple}
        If None, ``xp.linalg.pinv is called``. If "fro", a tolerance of
        ``1e-8 * xp.linalg.norm(x, "fro")`` is used. If a 2-tuple is provided,
        a tolerance of ``tol[1] * xp.linalg.norm(x, ord=tol[0])`` is used.
    Notes
    -----
    np.linalg.pinv     #<- uses SVD
    scipy.linalg.pinv  #<- uses a least-squares solver
    scipy.linalg.pinv2 #<- uses SVD
    In initial testing, accuracy seems similar.  np.linalg.pinv was fastest

    Based on Jeff Fessler's Matlab function of the same name.
    Python port by Gregory Lee.

    """
    xp, on_gpu = get_array_module(x, xp)
    if tol is None:
        p = xp.linalg.pinv(x)
    elif tol == "fro":
        p = xp.linalg.pinv(x, 1e-8 * xp.linalg.norm(x, "fro"))
    elif isinstance(tol, (list, tuple, xp.ndarray)) and len(tol) == 2:
        p = xp.linalg.pinv(x, tol[1] * xp.linalg.norm(x, ord=tol[0]))
    elif np.isscalar(tol):
        p = xp.linalg.pinv(x, tol)
    else:
        raise ValueError("unknown tolerance specifier for pinv_tol")
    return p


def outer_sum(a, b):
    """Outer sum.

    Equivalent to np.add.outer(a, b), but will also work for CuPy arrays.

    Returns
    -------
    s : ndarray
        ``s = a[:, np.newaxis] + b[np.newaxis, :]``
    """
    return a[:, np.newaxis] + b[np.newaxis, :]


def rss(a, axis=-1, keepdims=False, xp=None):
    """Root sum of squares along a specific axis (or axes).

    Parameters
    ----------
    a : array
        input data
    axis : tuple or int
        axis/axes to sum over
    keepdims : bool, optional
        If True, retain singleton axes.

    Returns
    -------
    out : array
        root sum of squares array
    """
    xp, on_gpu = get_array_module(a, xp)
    if a.dtype.kind == "c":
        a = (xp.conj(a) * a).real
    else:
        a = a * a
    if not xp.isscalar(axis):
        axis = tuple(axis)
    out = xp.sum(a, axis=axis, keepdims=keepdims)
    if out.ndim > 0:
        xp.sqrt(out, out=out)
    else:
        out = xp.sqrt(out)
    return out


def prod(seq):
    """Compute the product of the elements in seq.

    Parameters
    ----------
    seq : Sequence
        The sequence of values.

    Returns
    -------
    prod : scalar
        The product of the sequence of values.

    Notes
    -----
    This is a fast alternative to numpy.prod for short sequences.
    e.g. ``prod(arr.shape)`` has less overhead than ``numpy.prod(arr.shape)``.

    """
    return functools.reduce(mul, seq)


# TODO: remove the following try/except once minimum supported Python is 3.7
try:
    from contextlib import nullcontext
except ImportError:
    # implement nullcontext for Python 3.6
    from contextlib import AbstractContextManager

    # (copyied from Python 3.7)
    class nullcontext(AbstractContextManager):
        """Context manager that does no additional processing.

        Used as a stand-in for a normal context manager, when a particular
        block of code is only sometimes used with a normal context manager:
        """

        def __init__(self, enter_result=None):
            self.enter_result = enter_result

        def __enter__(self):
            return self.enter_result

        def __exit__(self, *excinfo):
            pass
