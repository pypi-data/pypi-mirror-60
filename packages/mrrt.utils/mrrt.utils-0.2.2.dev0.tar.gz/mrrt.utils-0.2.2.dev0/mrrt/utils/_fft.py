"""
FFT Utilities
=============

Functions for n-dimensional forward and inverse Fourier transforms.

If pyfftw is found, functions from ``pyfftw.interfaces`` are used to perform
transforms on CPU arrays. If ``pyFFTW`` is not found, ``scipy.fft`` will be
used when available. Otherwise ``numpy.fft`` is used.

When the input to these functions is a GPU Array, ``CuPy`` is used to perform
the transforms.

``fftnc`` and ``ifftnc`` are variants of ``fftn`` and ``ifftn`` with flexible
options for performing fftshifts pre and post transform.

Regardless which backend is used, all functions here give output in single
precision for single-precision inputs.

``build_fftn`` and ``build_ifftn`` are specific to FFTW-based transforms on the
CPU and are only available when pyFFTW is installed.


"""

# TODO: potentially add an FFT plan cache and/or add workers argument

import numpy as np

try:
    # SciPy 1.4.0+
    import scipy.fft

    fft_module = scipy.fft
    next_fast_len = scipy.fft.next_fast_len
except ImportError:
    import scipy.fftpack

    fft_module = np.fft
    # next_fast_len from older fftpack is a reasonable fallback choice
    next_fast_len = scipy.fftpack.next_fast_len

from ._cupy import get_array_module
from ._misc import define_if
from mrrt.utils import config

if config.have_cupy:
    import cupy


if config.have_pyfftw:
    import pyfftw

    # if the transform size is smaller than this, use a single thread
    single_thread_size_thresh = 100000

    # Turn on the cache for optimum performance
    pyfftw.interfaces.cache.enable()

    # increase cache preservation time from default of 0.1 seconds
    pyfftw.interfaces.cache.set_keepalive_time(5)

    # default effort when calling pyFFTW builder routines
    pyfftw_builder_effort = config.pyfftw_config.PLANNER_EFFORT
    pyfftw_threads = config.pyfftw_config.NUM_THREADS

    if hasattr(pyfftw.interfaces, "scipy_fft") and fft_module == scipy.fft:
        fftn_cpu = pyfftw.interfaces.scipy_fft.fftn
        ifftn_cpu = pyfftw.interfaces.scipy_fft.ifftn
    else:
        fftn_cpu = pyfftw.interfaces.numpy_fft.fftn
        ifftn_cpu = pyfftw.interfaces.numpy_fft.ifftn
    simd_alignment = pyfftw.simd_alignment

    next_fast_len = pyfftw.interfaces.scipy_fftpack.next_fast_len


if not config.have_pyfftw:
    pyfftw_threads = None
    pyfftw_builder_effort = None
    simd_alignment = None
    single_thread_size_thresh = None

    if fft_module == np.fft:
        # For numpy, have to modify output dtype to match pyFFTW behavior
        def _fftn(x, **kwargs):
            result_type = np.result_type(x.dtype, np.complex64)
            x = fft_module.fftn(x, **kwargs)
            return np.asarray(x, dtype=result_type)

        def _ifftn(x, **kwargs):
            result_type = np.result_type(x.dtype, np.complex64)
            x = fft_module.ifftn(x, **kwargs)
            return np.asarray(x, dtype=result_type)

    else:
        # call using set_workers context
        def _fftn(x, workers=-1, **kwargs):
            with fft_module.set_workers(workers):
                x = fft_module.fftn(x, **kwargs)
            return x

        def _ifftn(x, workers=-1, **kwargs):
            with fft_module.set_workers(workers):
                x = fft_module.ifftn(x, **kwargs)
            return x

    fftn_cpu = _fftn
    ifftn_cpu = _ifftn


__all__ = [
    "build_fftn",
    "build_ifftn",
    "fftn",
    "ifftn",  # n-dimensional FFT and IFFT
    "fftnc",
    "ifftnc",  # centered n-dimensional FFT and IFFT
    "fftshift",
    "ifftshift",  # FFT shifts
    "next_fast_len",
    "next_fast_len_multiple",
]


def fftnc(
    x,
    s=None,
    axes=None,
    norm=None,
    pre_shift_axes=None,
    post_shift_axes=None,
    xp=None,
):
    """Centered version of fftn.

    Parameters
    ----------
    a : array_like
        The array to transform
    s : sequence of ints, optional
        shape of the transform
    axes : sequence of ints, optional
        Specify which axes to tranform. The default is all axes.
    norm : {None, 'ortho'}, optional
        If None the forward transform is unscaled while the inverse is scaled
        by 1/N (where N is the product of the sizes of the transformed axes).
        If 'ortho', the forward and inverse transforms are scaled by 1/sqrt(N).
        In this case, the transform is unitary (preserves L2 norm).
    pre_shift_axes : sequence of ints, optional
        Specify which axes to call fftshift on prior to the transform. The
        default (None) will be to use the same value as for ``axes``.
    post_shift_axes : sequence of ints, optional
        Specify which axes to call fftshift on after the transform. The
        default (None) will be to use the same value as for ``axes``.

    Returns
    -------
    y : ndarray
        The transformed array.
    """
    xp, on_gpu = get_array_module(x, xp=xp)
    if xp is np:
        _fftshift = np.fft.fftshift
        _ifftshift = np.fft.ifftshift
        _fftn = fftn_cpu
    else:
        _fftshift = cupy.fft.fftshift
        _ifftshift = cupy.fft.ifftshift
        _fftn = cupy.fft.fftn
    if axes is not None and pre_shift_axes is None:
        pre_shift_axes = axes
    if axes is not None and post_shift_axes is None:
        post_shift_axes = axes
    if pre_shift_axes is None or pre_shift_axes:
        y = _ifftshift(x, axes=pre_shift_axes)
    else:
        y = x
    if on_gpu:
        # TODO: need to force contiguous manually?
        # y = xp.ascontiguousarray(y)
        pass
    y = _fftn(y, s=s, axes=axes, norm=norm)
    if post_shift_axes is None or post_shift_axes:
        y = _fftshift(y, axes=post_shift_axes)

    return y


def ifftnc(
    x,
    s=None,
    axes=None,
    norm=None,
    pre_shift_axes=None,
    post_shift_axes=None,
    xp=None,
):
    """Centered version of ifftn.

    Parameters
    ----------
    a : array_like
        The array to transform
    s : sequence of ints, optional
        shape of the transform
    axes : sequence of ints, optional
        Specify which axes to tranform. The default is all axes.
    norm : {None, 'ortho'}, optional
        If None the forward transform is unscaled while the inverse is scaled
        by 1/N (where N is the product of the sizes of the transformed axes).
        If 'ortho', the forward and inverse transforms are scaled by 1/sqrt(N).
        In this case, the transform is unitary (preserves L2 norm).
    pre_shift_axes : sequence of ints, optional
        Specify which axes to call fftshift on prior to the transform. The
        default (None) will be to use the same value as for ``axes``.
    post_shift_axes : sequence of ints, optional
        Specify which axes to call fftshift on after the transform. The
        default (None) will be to use the same value as for ``axes``.

    Returns
    -------
    y : ndarray
        The transformed array.
    """
    xp, on_gpu = get_array_module(x, xp=xp)
    if xp is np:
        _fftshift = np.fft.fftshift
        _ifftshift = np.fft.ifftshift
        _ifftn = ifftn_cpu
    else:
        _fftshift = cupy.fft.fftshift
        _ifftshift = cupy.fft.ifftshift
        _ifftn = cupy.fft.ifftn
    if axes is not None and pre_shift_axes is None:
        pre_shift_axes = axes
    if axes is not None and post_shift_axes is None:
        post_shift_axes = axes
    if pre_shift_axes is None or pre_shift_axes:
        y = _ifftshift(x, axes=pre_shift_axes)
    else:
        y = x
    if on_gpu:
        # y = xp.ascontiguousarray(y)
        pass
    y = _ifftn(y, s=s, axes=axes, norm=norm)
    if post_shift_axes is None or post_shift_axes:
        y = _fftshift(y, axes=post_shift_axes)
    return y


def fftn(x, s=None, axes=None, norm=None, xp=None):
    xp, on_gpu = get_array_module(x, xp=xp)
    if on_gpu:
        return cupy.fft.fftn(x, s=s, axes=axes, norm=norm)
    else:
        return fftn_cpu(x, s=s, axes=axes, norm=norm)


fftn.__doc__ = np.fft.fftn.__doc__


def ifftn(x, s=None, axes=None, norm=None, xp=None):
    xp, on_gpu = get_array_module(x, xp=xp)
    if on_gpu:
        return cupy.fft.ifftn(x, s=s, axes=axes, norm=norm)
    else:
        return ifftn_cpu(x, s=s, axes=axes, norm=norm)


ifftn.__doc__ = np.fft.ifftn.__doc__


def fftshift(x, axes, xp=None):
    xp, on_gpu = get_array_module(x, xp=xp)
    return xp.fft.fftshift(x, axes=axes)


fftshift.__doc__ = np.fft.fftshift.__doc__


def ifftshift(x, axes, xp=None):
    xp, on_gpu = get_array_module(x, xp=xp)
    return xp.fft.ifftshift(x, axes=axes)


ifftshift.__doc__ = np.fft.ifftshift.__doc__


@define_if(config.have_pyfftw, errmsg="build_fftn requires pyFFTW")
def build_fftn(
    a,
    axes=None,
    threads=pyfftw_threads,
    overwrite_input=False,
    planner_effort=pyfftw_builder_effort,
    **kwargs,
):
    """Convenience wrapper for pyfftw.builders.fftn."""
    return pyfftw.builders.fftn(
        a,
        axes=axes,
        threads=threads,
        overwrite_input=overwrite_input,
        planner_effort=planner_effort,
        **kwargs,
    )


@define_if(config.have_pyfftw, errmsg="build_fftn requires pyFFTW")
def build_ifftn(
    a,
    axes=None,
    threads=pyfftw_threads,
    overwrite_input=False,
    planner_effort=pyfftw_builder_effort,
    **kwargs,
):
    """Convenience wrapper for pyfftw.builders.ifftn."""
    return pyfftw.builders.ifftn(
        a,
        axes=axes,
        threads=threads,
        overwrite_input=overwrite_input,
        planner_effort=planner_effort,
        **kwargs,
    )


def next_fast_len_multiple(s, m=2):
    """Find the next fast FFT length that is a multiple of m.

    i.e. may want to prioritize a size that is a multiple of 2**n if an n-level
    wavelet transform is going to be performed on the same data.
    """
    fast_len = next_fast_len(s)
    while fast_len % m:
        fast_len = next_fast_len(fast_len + 1)
    return fast_len
