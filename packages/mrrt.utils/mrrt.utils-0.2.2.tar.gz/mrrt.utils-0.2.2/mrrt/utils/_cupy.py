import gc

import numpy as np

try:
    import cupy

    have_cupy = True
except ImportError:
    have_cupy = False


__all__ = [
    "free_pooled_gpu_memory",
    "free_pooled_memory",
    "free_pooled_pinned_memory",
    "get_array_module",
    "get_data_address",
    "get_free_memory",
    "have_cupy",
    "have_matching_data_ptr",
    "print_mempool_info",
]


def get_array_module(arr, xp=None):
    """ Check if the array is a cupy GPU array and return the array module.

    Paramters
    ---------
    arr : numpy.ndarray or cupy.core.core.ndarray
        The array to check.

    Returns
    -------
    array_module : python module
        This will be cupy when on_gpu is True and numpy otherwise.
    on_gpu : bool
        Boolean indicating whether the array is on the GPU.
    """
    if xp is None:
        if isinstance(arr, np.ndarray) or not have_cupy:
            return np, False
        else:
            xp = cupy.get_array_module(arr)
            return xp, (xp != np)
    else:
        return xp, (xp != np)


def get_data_address(x):
    """Returns memory address where a numpy or cupy array's data is stored."""
    if hasattr(x, "__array_interface__"):
        ptr_x = x.__array_interface__["data"][0]
    elif hasattr(x, "__cuda_array_interface__"):
        ptr_x = x.__cuda_array_interface__["data"][0]
    else:
        raise ValueError(
            "Input must have an __array_interface__ or "
            "__cuda_array_interface__ attribute."
        )
    return ptr_x


def have_matching_data_ptr(arr1, arr2):
    """Boolean indicating if arr1 and arr2 point to the same data."""
    return get_data_address(arr1) == get_data_address(arr2)


def _mem_unitconv(mem, units="MB"):
    """Convert memory from bytes to the specified unit.

    Parameters
    ----------
    mem : int
        The amount of memory in bytes.
    units : {'B', 'KB', 'MB', 'GB'}
        Specificy the units of the output ('B'=bytes, 'KB'=kilobytes,
        'MB=megabytes, 'GB'=gigabytes).

    Returns
    -------
    mem : float
        The amount of memory in the specified units.
    """
    if units.lower() == "b":
        return mem
    elif units.lower() == "kb":
        denom = 1024.0
    elif units.lower() == "mb":
        denom = 1024 * 1024.0
    elif units.lower() == "gb":
        denom = 1024 * 1024 * 1024.0
    else:
        raise ValueError(
            "units must be B, KB, MB or GB. (corresponding to "
            "bytes, kilobytes, megabytes, gigabytes)"
        )
    return mem / denom


def get_free_memory(units="MB"):
    """Returns the free memory of the currently active device.

    Parameters
    ----------
    units : {'B', 'KB', 'MB', 'GB'}
        The desired units (bytes, kilobytes, megabytes, gigabytes).

    Returns
    -------
    memory : float
        The amount of free memory in the specified units.
    """
    return _mem_unitconv(cupy.cuda.device.Device().mem_info[0], units)


def print_mempool_info():
    """Print some pooled memory attributes."""
    mempool = cupy.get_default_memory_pool()
    pinned_mempool = cupy.get_default_pinned_memory_pool()
    d = 1024 ** 3
    print("GPU memory pool:")
    print("\tused GB = {}".format(mempool.used_bytes() / d))
    print("\tfree GB = {}".format(mempool.free_bytes() / d))
    print("\ttotal GB = {}".format(mempool.total_bytes() / d))
    print("\tfree blocks = {}".format(mempool.n_free_blocks()))
    print("\tDevice free GB = {}".format(get_free_memory(units="GB")))

    print("\nCPU pinned memory pool:")
    print("\tfree blocks = {}".format(pinned_mempool.n_free_blocks()))


def free_pooled_gpu_memory(pool=None, verbose=True):
    """Free all memory in a GPU memory pool.

    Parameters
    ----------
    pool : cupy.cuda.memory.MemoryPool
        The memory pool. If None, the default CuPy memory pool is assumed.
    verbose : bool, optional
        If True, the memory before and after this operation is reported.
    """
    if pool is not None and not hasattr(pool, "free_all_blocks"):
        raise ValueError("pool to have a free_all_blocks method")
    else:
        pool = cupy.get_default_memory_pool()
    if verbose:
        mem_pre = get_free_memory(units="MB")
    pool.free_all_blocks()
    gc.collect()  # encourage it to be freed immediately
    if verbose:
        mem_post = get_free_memory(units="MB")
        print(f"free memory (pre) (MB) = {mem_pre}")
        print(f"free memory (post) (MB) = {mem_post}")


def free_pooled_pinned_memory(pool=None):
    """Free all memory in a CuPy pinned memory pool.

    Parameters
    ----------
    pool : cupy.cuda.pinned_memory.PinnedMemoryPool
        The pinned memory pool. If None, the default CuPy pinned memory pool is
        assumed.
    """
    if pool is not None and not hasattr(pool, "free_all_blocks"):
        raise ValueError("pool to have a free_all_blocks method")
    else:
        pool = cupy.get_default_pinned_memory_pool()
    pool.free_all_blocks()
    gc.collect()


def free_pooled_memory(verbose=False):
    """Frees both pooled GPU memory and pinned memory for the default pools.

    Parameters
    ----------
    verbose : bool, optional
        If True, the amount of free GPU memory both before and after this call
        is printed.

    """
    free_pooled_gpu_memory(verbose=verbose)
    free_pooled_pinned_memory()
