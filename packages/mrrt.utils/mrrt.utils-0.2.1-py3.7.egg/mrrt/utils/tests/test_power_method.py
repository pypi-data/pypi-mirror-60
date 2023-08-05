from itertools import product

import numpy as np
import pytest

from mrrt import utils

array_modules = [np]
if utils.config.have_cupy:
    import cupy

    array_modules += [cupy]


@pytest.mark.parametrize(
    "dtype, xp",
    product(
        [np.float32, np.float64, np.complex64, np.complex128], array_modules
    ),
)
def test_power_method_dtype(dtype, xp):
    lam = utils.power_method(xp.eye(16, dtype=dtype), dtype=dtype)
    assert abs(lam - 1) < 1e-5
    # lam is real and has the same precision
    assert lam.dtype is np.ones(1, dtype=dtype).real.dtype


def test_power_method_basic():
    lam = utils.power_method(np.eye(4))
    assert abs(lam - 1) < 1e-12

    b, lam = utils.power_method(np.eye(4), return_full=True)
    assert abs(lam - 1) < 1e-12
    assert b.ndim == 1


def test_power_method_errors():
    # non-square input
    with pytest.raises(ValueError):
        utils.power_method(np.random.randn(2, 3))

    # scalar input
    with pytest.raises(ValueError):
        utils.power_method(5)

    # non-2d input
    with pytest.raises(ValueError):
        utils.power_method(np.arange(8))


class Eye:
    def __init__(self, shape, xp=np):
        self.xp = xp
        self.shape = shape

    def norm(self, x):
        return x


@pytest.mark.parametrize("xp", array_modules)
def test_power_method_A_op(xp):
    A = Eye((16, 16), xp=xp)
    lam = utils.power_method(A)
    assert abs(lam - 1.0) < 1e-5
