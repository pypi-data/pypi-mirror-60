from itertools import product

import numpy as np
from numpy.testing import assert_equal
import pytest

from mrrt.utils import config, fftn, fftnc, ifftn, ifftnc, fftshift, ifftshift
from mrrt.utils import next_fast_len_multiple

# TODO: may want to set pyFFTW to use 1 thread for the small transform sizes
# used here.
# TODO: add tests cases for build_fftn, build_ifftn

array_modules = [np]
if config.have_cupy:
    import cupy

    array_modules += [cupy]


@pytest.mark.parametrize(
    "xp, norm, axes, pre_shift, post_shift, dtype",
    product(
        array_modules,
        ["ortho", None],  # norm
        [None, (0,), (1, 2)],  # axes
        [None, (), (0, 1, 2)],  # pre_shift
        [None, ()],  # post_shift
        [np.float32, np.float64, np.complex64, np.complex128],  # dtype
    ),
)
def test_fftnc_ifftnc(xp, norm, axes, pre_shift, post_shift, dtype):
    rstate = xp.random.RandomState(1234)
    # test with at least one odd-sized axis

    shape = (15, 32, 18)
    x = rstate.standard_normal(shape).astype(dtype, copy=False)
    if x.dtype.kind == "c":
        x += 1j * rstate.standard_normal(shape).astype(dtype, copy=False)

    if dtype in [np.float32, np.complex64]:
        rtol = atol = 1e-4
    else:
        rtol = atol = 1e-12

    # default shift behavior is to shift all axes that are transformed
    if pre_shift is None:
        expected_pre_shift = axes
    else:
        expected_pre_shift = pre_shift

    if post_shift is None:
        expected_post_shift = axes
    else:
        expected_post_shift = post_shift

    x_cpu = x if xp is np else x.get()
    # compare to numpy.fft.fftn result on CPU
    expected_result = fftshift(
        np.fft.fftn(
            ifftshift(x_cpu, axes=expected_pre_shift), axes=axes, norm=norm
        ),
        axes=expected_post_shift,
    )

    # Verify agreement with expected numpy.fft.fftn result
    res = fftnc(
        x,
        axes=axes,
        norm=norm,
        pre_shift_axes=pre_shift,
        post_shift_axes=post_shift,
    )
    xp.testing.assert_allclose(res, expected_result, rtol=rtol, atol=atol)

    # Verify correct round trip
    # note: swap pre/post shift vars relative to the forward transform
    rec = ifftnc(
        res,
        axes=axes,
        norm=norm,
        pre_shift_axes=post_shift,
        post_shift_axes=pre_shift,
    )
    xp.testing.assert_allclose(x, rec, rtol=rtol, atol=atol)


@pytest.mark.parametrize("xp", array_modules)
def test_fft_output_dtype(xp):
    x = xp.random.randn(256)
    y = fftn(x, axes=None, norm="ortho", xp=xp)
    assert_equal(y.dtype, xp.complex128)
    r = ifftn(y, axes=None, norm="ortho", xp=xp)
    assert_equal(r.dtype, xp.complex128)

    x = xp.random.randn(256).astype(np.complex128)
    y = fftn(x, axes=None, norm="ortho", xp=xp)
    assert_equal(y.dtype, xp.complex128)
    r = ifftn(y, axes=None, norm="ortho", xp=xp)
    assert_equal(r.dtype, xp.complex128)

    for dtype in [xp.float16, xp.float32, xp.complex64]:
        x = xp.random.randn(256).astype(dtype)
        y = fftn(x, axes=None, norm="ortho", xp=xp)
        assert_equal(y.dtype, xp.complex64)

        r = ifftn(y, axes=None, norm="ortho", xp=xp)
        assert_equal(r.dtype, xp.complex64)


@pytest.mark.parametrize("m", [1, 2, 3, 8])
def test_next_fast_len_multiple(m):
    sizes = range(1, 35)
    fast_sizes = [next_fast_len_multiple(s, m) for s in sizes]
    # fast size is a multiple of m
    assert all(fs % m == 0 for fs in fast_sizes)
    # fast size is >= to the original size
    assert all(fs >= s for fs, s in zip(fast_sizes, sizes))
