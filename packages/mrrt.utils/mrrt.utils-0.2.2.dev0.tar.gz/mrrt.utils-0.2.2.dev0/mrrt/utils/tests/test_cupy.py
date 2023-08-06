from numbers import Integral

import numpy as np
import pytest

from mrrt import utils
from mrrt.utils import config

array_modules = [np]
if config.have_cupy:
    import cupy

    array_modules += [cupy]


@pytest.mark.parametrize("xp", array_modules)
def test_get_array_module(xp):
    x = xp.arange(8)
    xp_detected, on_gpu = utils.get_array_module(x)
    assert xp is xp_detected


@pytest.mark.skipif(not config.have_cupy, reason="cupy not available")
def test_get_array_module_special_cases():
    # fallback to user-provided xp
    xp, on_gpu = utils.get_array_module(None, np)
    assert xp is np

    # non-array type should be np
    xp_detected, on_gpu = utils.get_array_module([5, 2, 1])
    assert xp is np
    assert ~on_gpu


@pytest.mark.parametrize("xp", array_modules)
def test_get_data_address(xp):
    x = xp.arange(8)
    ptr = utils.get_data_address(x)
    assert isinstance(ptr, Integral)

    with pytest.raises(ValueError):
        utils.get_data_address([1, 2, 3])


@pytest.mark.skipif(not config.have_cupy, reason="cupy not available")
def test_get_free_memory():
    mem_bytes = utils.get_free_memory("B")
    mem_kb = utils.get_free_memory("KB")
    assert mem_bytes > mem_kb
    mem_mb = utils.get_free_memory("MB")
    assert mem_kb > mem_mb
    mem_gb = utils.get_free_memory("GB")
    assert mem_mb > mem_gb

    with pytest.raises(ValueError):
        utils.get_free_memory("unknown")


@pytest.mark.skipif(not config.have_cupy, reason="cupy not available")
def test_print_mempool_info():
    utils.print_mempool_info()


@pytest.mark.skipif(not config.have_cupy, reason="cupy not available")
@pytest.mark.parametrize("verbose", [False, True])
def test_free_pooled_memory(verbose):
    a = cupy.arange(int(1e6))
    del a
    utils.free_pooled_memory()


@pytest.mark.skipif(not config.have_cupy, reason="cupy not available")
def test_free_pooled_gpu_memory():
    a = cupy.arange(int(1e6))
    del a
    utils.free_pooled_gpu_memory()
    with pytest.raises(ValueError):
        utils.free_pooled_gpu_memory(pool="invalid")


@pytest.mark.skipif(not config.have_cupy, reason="cupy not available")
def test_free_pooled_pinned_memory():
    a = cupy.arange(int(1e6))
    a = a.get()
    del a
    utils.free_pooled_pinned_memory()
    with pytest.raises(ValueError):
        utils.free_pooled_pinned_memory(pool="invalid")
