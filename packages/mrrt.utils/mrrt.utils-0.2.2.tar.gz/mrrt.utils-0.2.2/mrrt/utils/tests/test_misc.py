from itertools import product

import numpy as np
from numpy import testing
import pytest

from mrrt import utils

array_modules = [np]
if utils.config.have_cupy:
    import cupy

    array_modules += [cupy]


def test_complexify():
    xd = np.ones(4)
    xc = utils.complexify(xd)
    testing.assert_equal(xc.dtype, np.complex128)

    xf = xd.astype(np.float32)
    xfc = utils.complexify(xf)
    testing.assert_equal(xfc.dtype, np.complex64)
    xfc = utils.complexify(xf, complex_dtype=np.complex128)
    testing.assert_equal(xfc.dtype, np.complex128)


def test_reale():
    for real_dtype in [np.float32, np.float64]:
        for offset_mult in [1, 999, 1001, 1e4]:
            eps = np.finfo(real_dtype).eps * offset_mult
            cplx_dtype = np.result_type(real_dtype, np.complex64)
            x = [1 + 1j * eps]
            x = np.asarray(x, dtype=cplx_dtype)
            assert utils.reale(x.real) == 1
            if offset_mult >= 1e3:
                testing.assert_raises(RuntimeError, utils.reale, x, com="error")
                testing.assert_warns(UserWarning, utils.reale, x, com="warn")
                utils.reale(x, com="display")
            else:
                assert utils.reale(x) == 1


@pytest.mark.parametrize("xp", array_modules)
def test_jinc(xp, show_figure=False):
    # should work with scalar, list or array input
    utils.jinc(5)
    utils.jinc([5])
    y = utils.jinc(xp.linspace(-15, 15, int(1e3)))
    assert isinstance(y, xp.ndarray)

    if show_figure:
        from matplotlib import pyplot as plt

        # plot result with numpy array input
        plt.plot(utils.jinc(xp.linspace(-15, 15, 1e3)))


@pytest.mark.parametrize("xp", array_modules)
def test_rect(xp):
    x = utils.rect(xp.linspace(-2, 2, 100))
    assert x.min() == 0
    assert x.max() == 1


@pytest.mark.parametrize("xp", array_modules)
def test_max_percent_diff(xp):
    a = xp.full((16,), 100.0)
    b = a.copy()
    b[5] += 1
    d = utils.max_percent_diff(a, b, use_both=False)
    assert d == 1

    d = utils.max_percent_diff(a, b, use_both=True)
    assert d < 1

    # shape mismatch
    with pytest.raises(ValueError):
        utils.max_percent_diff(a, b[:-1])


@pytest.mark.parametrize(
    "xp, tol", product(array_modules, [None, "fro", (1, 1e-4)])
)
def test_pinv_tol(xp, tol):
    e = xp.eye(5)
    xp.testing.assert_allclose(e, utils.pinv_tol(e, tol=tol))


@pytest.mark.skipif(not utils.config.have_cupy, reason="cupy is required")
@pytest.mark.parametrize(
    "dtype", [np.float32, np.float64, np.complex64, np.complex128]
)
def test_pinv_compare_cupy(dtype):
    rstate = np.random.RandomState(5)
    r = rstate.standard_normal((32, 32)).astype(dtype)
    if np.dtype(dtype).kind == "c":
        r = r + 1j * rstate.standard_normal((32, 32)).astype(dtype)
    rg = cupy.asarray(r)

    r_inv = utils.pinv_tol(r)
    rg_inv = utils.pinv_tol(rg)

    atol = rtol = np.finfo(np.dtype(dtype)).eps * 500
    np.testing.assert_allclose(r_inv, rg_inv.get(), atol=atol, rtol=rtol)


def test_outer_sum():
    a = np.random.randn(16)
    b = np.random.randn(8)
    np.testing.assert_allclose(utils.outer_sum(a, b), np.add.outer(a, b))


@pytest.mark.skipif(not utils.config.have_cupy, reason="cupy is required")
def test_compare_outer_sum():
    a = np.random.randn(16)
    b = np.random.randn(8)
    ag = cupy.asarray(a)
    bg = cupy.asarray(b)
    cupy.testing.assert_allclose(utils.outer_sum(a, b), utils.outer_sum(ag, bg))


@pytest.mark.parametrize(
    "xp, dtype, axis, keepdims",
    product(
        array_modules,
        [np.float32, np.float64, np.complex64, np.complex128],
        [0, (-1,), (0, 1)],
        [False, True],
    ),
)
def test_rss(xp, dtype, axis, keepdims):
    rstate = xp.random.RandomState(0)
    x = rstate.randn(16, 32).astype(dtype)
    if x.dtype.kind == "c":
        x = x + 1j * rstate.randn(16, 32).astype(dtype)
    tol = np.finfo(dtype).eps * 10

    if utils.config.have_cupy:
        # disable CUB here until cupy/cupy#2720 is addressed
        cub_value = cupy.cuda.cub_enabled
        cupy.cuda.cub_enabled = False

    try:
        y_expected = np.sqrt(
            np.sum(np.abs(x) ** 2, axis=axis, keepdims=keepdims)
        )
        y = utils.rss(x, axis=axis, keepdims=keepdims)
        if keepdims:
            assert y.ndim == x.ndim
        xp.testing.assert_allclose(y, y_expected, atol=tol, rtol=tol)
    finally:
        if utils.config.have_cupy:
            cupy.cuda.cub_enabled = cub_value


@pytest.mark.parametrize("seq", [(1, 2, 3), [1, 2, 3], np.arange(5)])
def test_prod(seq):
    assert utils.prod(seq) == np.prod(seq)
