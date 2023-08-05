"""
.. currentmodule:: mrrt.utils


FFT utilities
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
CPU.

.. autosummary::
   :toctree: generated/

   fftn
   ifftn
   fftnc
   ifftnc
   build_fftn
   build_ifftn
   fftshift
   ifftshift
   next_fast_len
   next_fast_len_multiple

Histograms
==========

.. autosummary::
   :toctree: generated/

   hist_equal


Array Masks / Embedding
=======================

.. autosummary::
   :toctree: generated/

   embed
   masker

.. autosummary::
   :template: class.rst
   :toctree: generated/

   ArrayMasker

Phantoms
========

.. autosummary::
   :template: class.rst
   :toctree: generated/

   ImageGeometry

.. autosummary::
   :toctree: generated/

   ellipse_im

Miscellaneous
=============

.. autosummary::
   :toctree: generated/

   complexify
   define_if
   jinc
   max_percent_diff
   nullcontext
   outer_sum
   pinv_tol
   prod
   profile
   reale
   rect
   rss

Linear Algebra
==============

.. autosummary::
   :toctree: generated/

   power_method


GPU Utilities
=============

.. autosummary::
   :toctree: generated/

   free_pooled_gpu_memory
   free_pooled_memory
   free_pooled_pinned_memory
   get_array_module
   get_data_address
   get_free_memory
   have_cupy
   have_matching_data_ptr
   print_mempool_info

"""
from . import config  # noqa
from ._cupy import *  # noqa
from ._fft import *  # noqa
from ._hist import *  # noqa
from ._masking import *  # noqa
from ._misc import *  # noqa
from ._phantom import *  # noqa
from ._power_method import *  # noqa
from .version import __version__  # noqa
