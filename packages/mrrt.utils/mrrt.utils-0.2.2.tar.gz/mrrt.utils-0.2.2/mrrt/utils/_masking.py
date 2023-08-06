import numpy as np

from ._cupy import get_array_module


__all__ = ["embed", "mask", "masker", "ArrayMasker"]


def _mask_first_axes(x, mask, c_contig=None):
    """Fast application of the mask for both C or Fortran-ordered x.
    """
    if c_contig is None:
        c_contig = x.flags.c_contiguous
    if c_contig:
        y = x[mask]
    else:
        # same values as x[mask], but in a different order
        # This seems to improve memory access efficiency
        shape = (mask.size,) + x.shape[mask.ndim :]
        y = x.reshape(shape, order="F")[mask.ravel("F")]
    return y, c_contig


def _embed_first(
    y, mask, nmask, nreps, shape_out, c_contig, squeeze_output, xp
):
    if c_contig:
        if squeeze_output and nreps == 1:
            y = y.reshape((nmask,), order="C")
            z = xp.zeros(shape_out, dtype=y.dtype)
            z[mask] = y
        else:
            y = y.reshape((nmask, nreps), order="C")
            z = xp.zeros(mask.shape + (nreps,), dtype=y.dtype, order="C")
            z[mask, :] = y
            z = z.reshape(shape_out)
    else:
        y = y.reshape((nmask, nreps), order="F")
        z = xp.zeros((mask.size, nreps), dtype=y.dtype, order="F")
        if nreps > 1:
            z[mask.ravel(order="F"), :] = y.reshape((-1, nreps), order="F")
        else:
            z[mask.ravel(order="F"), :] = y
        # if squeeze_output and nreps == 1:
        #     shape_out = mask.shape
        # else:
        #     shape_out = mask.shape + (-1,)
        z = z.reshape(shape_out, order="F")
    return z


class ArrayMasker(object):
    """Forward and inverse masker for n-dimensional arrays.

    Parameters
    ----------
    mask : ndarray or None
        The mask to be applied. If None, this operator does nothing.
    mask_first_axes : bool, optional
        If True, the mask corresponds to the first ``mask.ndim`` axes of the
        array. Otherwise, the mask corresponds to the last ``mask.ndim`` axes.
    order : {'C', 'F', None}
        This determines the contiguity mode to be used by the masking function.
        Generally, this should be None to allow automatic selection based on
        the array contiguity present on the first call to ``masker``.
    xp : {np, cupy}
        The array module.

    Notes
    -----
    This is a class that stores a mask and can be used to either extract
    (or embed) values corresponding to the mask from arrays of the
    corresponding shape.
    """

    def __init__(self, mask, mask_first_axes=True, order=None, xp=None):
        self.mask = mask
        self.mask_first_axes = mask_first_axes
        self.c_contig = None
        # print(f"order={order}, c_contig={self.c_contig}")
        if order is not None:
            if order not in ["F", "C"]:
                raise ValueError(f"Invalid order, '{order}', specified")
            self.c_contig = order == "C"
        else:
            self.c_contig = None  # To be determined upon first use
        # print(f"order={order}, c_contig={self.c_contig}")
        self.order = order

        if mask is None:
            self.xp = None
            self.nmask = None
            self.mask = None
        else:
            self.xp, _ = get_array_module(mask, xp)
            self.mask = self.xp.asarray(mask)
            nmask = self.mask.sum()
            if self.xp != np:
                nmask = nmask.get()
            self.nmask = nmask

    def masker(self, x, atleast2d=False):
        """Apply the mask to array x.

        Parameters
        ----------
        x : ndarray
            The array to mask.
        atleast2d : bool, optional
            If True, convert 1d output to a column vector (shape 1 on second
            axis).

        Returns
        -------
        y : ndarray
            The masked array.
        """
        mask = self.mask
        if mask is None:
            return x
        # self.embed_shape = x.shape  # compute in embed, so it is not dependent on the input to masker

        # TODO: check device here
        xp, _ = get_array_module(x, self.xp)

        if x.ndim < mask.ndim and x.size == mask.size:
            # reshape raveled inputs to match the shape of the mask
            if self.order in ["F", None]:
                x = x.reshape(mask.shape, order="F")
            else:
                x = x.reshape(mask.shape, order="C")

        if self.mask_first_axes:
            if x.ndim < mask.ndim or x.shape[: mask.ndim] != mask.shape:
                raise ValueError("mask shape mismatch")
            masked, self.c_contig = _mask_first_axes(x, mask, self.c_contig)
        else:
            if x.ndim < mask.ndim or x.shape[-mask.ndim :] != mask.shape:
                raise ValueError("mask shape mismatch")
            x, mask = map(np.transpose, (x, mask))
            masked, self.c_contig = _mask_first_axes(x, mask, self.c_contig)
            masked = masked.transpose()

        if atleast2d and masked.ndim == 1:
            if self.mask_first_axes:
                masked = masked[..., np.newaxis]
            else:
                masked = masked[np.newaxis, ...]

        # if self.order is not None:
        #     if self.order == "C" and not masked.flags.c_contiguous:
        #         masked = self.xp.ascontiguousarray(masked)
        #     elif not masked.flags.f_contiguous:
        #         masked = self.xp.asfortranarray(masked)
        return masked

    def embed(self, y, squeeze_output=True):
        """Embed y into the mask, returning a new array.

        Parameters
        ----------
        y : ndarray
            The values corresponding to the mask.
        squeeze_output : bool, optional
            If True, any 1d axes after embedding are squeezed.

        Returns
        -------
        x : ndarray
            The full array containin the embedded values.
        """
        if self.mask is None:
            return y

        xp = self.xp
        nrep = y.size // self.nmask
        if nrep < 1 or y.size % self.nmask != 0:
            raise ValueError("invalid size")
        if not hasattr(
            self, "embed_shape"
        ):  # TODO: allow specifying embed_shape via __init__?
            if self.mask_first_axes:
                if nrep == 1 and squeeze_output:
                    rep_shape = ()
                else:
                    rep_shape = y.shape[1:] if y.ndim > 1 else (nrep,)
                self.embed_shape = self.mask.shape + rep_shape
            else:
                if nrep == 1 and squeeze_output:
                    rep_shape = ()
                else:
                    rep_shape = y.shape[:-1] if y.ndim > 1 else (nrep,)
                self.embed_shape = rep_shape + self.mask.shape

        if self.mask_first_axes:
            mask = self.mask
            s = self.embed_shape
            z = _embed_first(
                y, mask, self.nmask, nrep, s, self.c_contig, squeeze_output, xp
            )
            if not squeeze_output and self.mask.ndim == z.ndim:
                z = z[..., np.newaxis]
        else:
            y, mask = map(self.xp.transpose, (y, self.mask))
            s = self.embed_shape[::-1]
            z = _embed_first(
                y, mask, self.nmask, nrep, s, self.c_contig, squeeze_output, xp
            )
            z = z.transpose()
            if not squeeze_output and self.mask.ndim == z.ndim:
                z = z[np.newaxis, ...]
        return z


def mask(x, mask, order="F", squeeze_output=True, xp=None):
    """Extract masked values from x.

    Parameters
    ----------
    x : ndarray
        The data to mask.
    mask : ndarray
        A boolean array corresponding to the mask
    order : {'F', 'C'}, optional
        The order used when raveling arrays.
    squeeze_output : bool, optional
        If False, the output will always be at least 2d.
    xp : {numpy, cupy}
        The array module.
    """
    xp, on_gpu = get_array_module(x, xp)
    if True:
        mask_first_axes = order == "F"
    else:
        # legacy order="C" was using this (undesired) case
        mask_first_axes = True
    atleast2d = not squeeze_output
    M = ArrayMasker(mask, mask_first_axes=mask_first_axes, order=order, xp=xp)
    return M.masker(x, atleast2d=atleast2d)


masker = mask


def embed(
    x, mask=None, order="F", prod_dim=False, squeeze_output=True, xp=None
):
    """Embed data into an existing mask.

    Parameters
    ----------
    x : ndarray
        The data to embed in a new array via the specified `mask`.
    mask : ndarray
        A boolean array corresponding to the mask
    order : {'F', 'C'}, optional
        The order used when raveling arrays.
    prod_dim : bool, optional
        TODO
    squeeze_output : bool, optional
        If False, the output will always be at least 2d.
    xp : {numpy, cupy}
        The array module.
    """
    xp, on_gpu = get_array_module(x, xp)
    if True:
        mask_first_axes = order == "F"
    else:
        # legacy order="C" was using this (undesired) case
        mask_first_axes = True
    M = ArrayMasker(mask, mask_first_axes=mask_first_axes, order=order, xp=xp)
    return M.embed(x, squeeze_output=squeeze_output)
