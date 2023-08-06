from math import cos, sin, ceil

import numpy as np
from numpy.testing import assert_allclose

from ._masking import ArrayMasker


__all__ = ["ellipse_im", "ImageGeometry"]


def _shepp_logan_parameters(xfov, yfov):
    """Ellipse parameters for the Shepp Logan phantom.

    Notes
    -----
    The first four columns are unitless "fractions of field of view".

    References
    ----------
    .. [1] A.C. Kak and M. Slaney. Principles of Computerized Tomographic
        Imaging. 2001, Society for Industrial and Applied Mathematics.
        :DOI:10.1137/1.9780898719277
    """

    # fmt: off
    params = np.array(
        [
            [0,      0,      0.92,   0.69,    90,  2],  # noqa E241
            [0,     -0.0184, 0.874,  0.6624,  90,  -0.98],  # noqa E241
            [0.22,   0,      0.31,   0.11,    72,  -0.02],  # noqa E241
            [-0.22,  0,      0.41,   0.16,    108, -0.02],  # noqa E241
            [0,      0.35,   0.25,   0.21,    90,  0.01],  # noqa E241
            [0,      0.1,    0.046,  0.046,    0,  0.01],  # noqa E241
            [0,     -0.1,    0.046,  0.046,    0,  0.01],  # noqa E241
            [-0.08, -0.605,  0.046,  0.023,    0,  0.01],  # noqa E241
            [0,     -0.605,  0.023,  0.023,    0,  0.01],  # noqa E241
            [0.06,  -0.605,  0.046,  0.023,   90,  0.01],  # noqa E241
        ]
    )
    # fmt: on

    params[:, [0, 2]] *= np.asarray(xfov) / 2
    params[:, [1, 3]] *= np.asarray(yfov) / 2
    return params


def _ellipse_im(shape, params, distances, offsets, rot, over, replace):
    """Generate an Ellipse-based phantom based on params."""
    nx, ny = shape
    dx, dy = distances
    offset_x, offset_y = offsets

    if params.shape[1] != 6:
        raise ValueError(
            "Error in %s: bad ellipse parameter vector size" % __name__
        )

    if over < 1 or (over % 1 != 0):
        raise ValueError("over must be an integer >= 1")

    # optional rotation
    if rot != 0:
        th = np.deg2rad(rot)
        cx = params[:, 0]
        cy = params[:, 1]
        params[:, 0] = cx * cos(th) + cy * sin(th)
        params[:, 1] = -cx * sin(th) + cy * cos(th)
        params[:, 4] = params[:, 4] + rot

    phantom = np.zeros((nx * over, ny * over))

    wx = (nx * over - 1) / 2.0 + offset_x * over
    wy = (ny * over - 1) / 2.0 + offset_y * over
    xx = (np.arange(0, nx * over) - wx) * dx / over
    yy = (np.arange(0, ny * over) - wy) * dy / over
    xx, yy = np.meshgrid(xx, yy, indexing="ij", sparse=True)

    for i in range(params.shape[0]):
        ellipse = params[i, :]
        cx = ellipse[0]
        rx = ellipse[2]
        cy = ellipse[1]
        ry = ellipse[3]
        theta = np.deg2rad(ellipse[4])
        x = cos(theta) * (xx - cx) + sin(theta) * (yy - cy)
        y = -sin(theta) * (xx - cx) + cos(theta) * (yy - cy)
        tmp = np.power((x / rx), 2) + np.power((y / ry), 2) <= 1
        if replace:
            phantom[tmp > 0] = ellipse[5]
        else:
            phantom = phantom + ellipse[5] * tmp
    if over != 1:
        sl_down = tuple([slice(0, s, over) for s in phantom.shape])
        phantom = phantom[sl_down]
    return phantom, params


def ellipse_im(
    ig, params="shepplogan-mod", rot=0, oversample=1, scale=1.0, fov=250,
):
    """Generate an ellipse phantom image from parameters.

    Parameters
    ----------
    ig : ImageGeometry object
        This object will determine the phantom shape and position.
        Specifically, the attributes ``ig.shape``, ``ig.distances`` and
        ``ig.offsets`` are used.
    params : array or {}
        If an array is provided it must be shape ``(n, 6)`` where ``n``
        indicates the number of ellipses and the 6 columns correspond to
        properties of each ellipse:
        ``x_center, y_center, x_radius, y_radius, angle_degrees, amplitude``.
        Where the first four columns are a dimensionless fraction of ``fov``.

        This can also be a string describing one of the following variants of
        the Shepp-Logan phantom [1]_:

        - **"shepplogan"**: The original Shepp-Logan phantom. Set ``scale=1000``
          to scale this to Hounsfield units.

        - **"shepplogan-mod"**: A version with the relative intensities within
          the object covering a wider range. This may be more suitable than the
          orginal as an MRI phantom

        - **"shepplogan-emis"**: A variant with intensities intended for use an
          emission tomography phantom.

    rot : float, optional
        Apply a rotation (in degrees) to the phantom.
    oversample : int, optional
        Can be used to set an oversampling factor used during analytical
        phantom generation. Does not modify the final shape of the generated
        phantom.
    scale : float, optional
        A scalar multiplier for the amplitude of the generated phantom.
    fov : float or None, optional
        The field of view (in mm). If this is set to ``None``, the fov
        attribute of ``ImageGeometry`` will be used instead.

    Returns
    -------
    phantom : ndarray
        A 2d array corresponding to the specified phantom.

    References
    ----------
    .. [1] L. A. Shepp and B. F. Logan. The Fourier reconstruction of a head
        section. IEEE Transactions on Nuclear Science, 1974. 21(3):21-43.
        :DOI:10.1109/TNS.1974.6499235

    """
    if not isinstance(ig, ImageGeometry):
        raise ValueError("ig must be an ImageGeometry object")

    if params is None:
        print("No ellipse parameters specified, using defaults")

    if fov is None:
        fov = ig.fov

    if isinstance(params, str):
        if params == "shepplogan":
            params = _shepp_logan_parameters(fov, fov)
        elif params == "shepplogan-mod":
            params = _shepp_logan_parameters(fov, fov)
            params[:, 5] = [1, -0.8, -0.2, -0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        elif params == "shepplogan-emis":
            params = _shepp_logan_parameters(fov, fov)
            params[:, 5] = [1, 1, -2, 2, 3, 4, 5, 6, 1, 1]
            params = np.array(params)

    params = np.asanyarray(params)
    if params.ndim == 1:
        params.shape = (1, params.shape[0])  # needs to be a 1x6 array
    # else:
    params[:, 5] = params[:, 5] * scale

    phantom, params = _ellipse_im(
        shape=ig.shape,
        params=params,
        distances=ig.distances,
        offsets=ig.offsets,
        rot=rot,
        over=oversample,
        replace=False,
    )
    return phantom, params


def _tuple_or_none(x, ndim):
    """If x is not None, broadcast x to a tuple of length ndim."""
    if x is None:
        return None
    if np.isscalar(x):
        x = (x,) * ndim
    return tuple(x)


class ImageGeometry(object):

    """Class representing n-dimensional image geometry.

    Parameters
    ----------
    shape : tuple of int
        The image shape.
    distances : tuple of int
        The pixel spacing along each axis. If an integer is provided, the same
        value is used for all axes. Either ``distances`` or ``fov`` must be
        provided.
    offsets : 'dsp' or tuple of int
        When offsets = 0, the discrete grid is sampled symmetrically about 0 on
        each axis. Setting this to 'dsp' is equivelent to setting it to
        ``(0.5,) * len(shape)`` and gives a grid that runs from:
        np.arange(-ceil(s//2), floor(s/2)) for an axis of length ``s``. If an
        integer is provided, the same value is used for all axes.
    fov : tuple of int
        The field of view along each axis.
    mask : ndarray or None
        A logical support mask for the object.
    """

    def __init__(
        self,
        shape,
        distances=None,
        offsets="dsp",
        down=1,
        mask=None,
        fov=None,
        order="F",
        xp=np,
    ):
        # if len(kwargs.keys()) is 0:
        # ImageGeometry_test()  #TODO:  how to call test for object?

        if distances is None and fov is None:
            raise ValueError(
                "ImageGeometry requires either distances or fov "
                "to be specified."
            )

        if np.any([s % 1 != 0 for s in shape]):
            self.shape = shape
        self.shape = tuple([int(s) for s in shape])
        if len(shape) < 1:
            raise ValueError("empty shape")
        self.size = np.prod(self.shape)
        self.ndim = len(self.shape)
        self.xp = xp

        distances = _tuple_or_none(distances, self.ndim)
        fov = _tuple_or_none(fov, self.ndim)
        if distances is None:
            if fov is None:
                raise ValueError("either distances or fov must be specified")
            distances = tuple([f / s for f, s in zip(fov, self.shape)])
        elif fov is None:
            fov = tuple([d * s for d, s in zip(distances, self.shape)])
        else:
            if not assert_allclose(
                np.asarray(self.shape) * np.asarray(self.distances),
                np.asarray(fov),
            ):
                raise ValueError("Inconsistent shape, fov, distances.")

        self.distances = distances
        self.fov = fov
        if len(self.fov) != len(self.distances) != len(self.shape):
            raise ValueError("fov, distances, shape must have equal length")

        if offsets == "dsp":
            offsets = (0.5,) * self.ndim
        elif np.isscalar(offsets):
            offsets = (offsets,) * self.ndim
        self.offsets = tuple(offsets)

        self.order = order
        if self.order not in ["F", "C"]:
            raise ValueError("order must be 'F' or 'C'")

        # mask
        if mask is None:
            mask = self.xp.ones(self.shape, dtype=np.bool)
        else:
            mask = self.xp.asarray(mask)
            if mask.dtype != bool:
                raise ValueError("mask must be boolean or None")
            if mask.shape != self.shape:
                raise ValueError("mask.shape must match shape")
        self.mask = mask
        self.Masker = ArrayMasker(mask, mask_first_axes=True, xp=self.xp)

    @property
    def nx(self):
        """Size along the 1st dimension."""
        return self.shape[0]

    @property
    def ny(self):
        """Size along the 2nd dimension."""
        if self.ndim > 1:
            return self.shape[1]
        else:
            return 1

    @property
    def nz(self):
        """Size along the 3rd dimension."""
        if self.ndim > 2:
            return self.shape[2]
        else:
            return 1

    @property
    def nmask(self):
        """The number of pixels in the image mask."""
        return self.mask.sum()

    def embed(self, x, order=None):
        """Create a new array, embedding x based on the mask."""
        return self.Masker.embed(x)

    def masker(self, x):
        """Apply the mask to x."""
        return self.Masker.masker(x)

    def _fg_axis(self, axis, centered=True):
        """Get frequency sampling points for a single axis."""
        axis = axis % self.ndim
        n = self.shape[axis]
        d = self.distances[axis]
        if centered:
            # return np.fft.fftshift(np.fft.fftfreq(n, d))
            return self.xp.arange(-(n // 2), ceil(n / 2)) / (n * d)
        else:
            return self.xp.fft.fftfreq(n, d)

    def fgrid(self, axes=None, indexing="ij", sparse=True):
        """DFT frequency sample grid."""
        if axes is None:
            axes = self.xp.arange(self.ndim)
        fg = [self._fg_axis(axis=a, centered=True) for a in range(self.ndim)]
        fg = self.xp.meshgrid(*fg, indexing=indexing, sparse=sparse)
        return fg

    def _grid_axis(self, axis):
        """Image-domain coordinates along a given axis."""
        axis = axis % self.ndim
        n = self.shape[axis]
        offset = self.offsets[axis]
        d = self.distances[axis]
        wx = (n - 1) / 2 + offset
        x = (self.xp.arange(n) - wx) * d
        return x

    def grid(self, axes=None, indexing="ij", sparse=True):
        """Image domain coordinates."""
        if axes is None:
            axes = self.xp.arange(self.ndim)
        grid = [self._grid_axis(a) for a in axes]
        grid = self.xp.meshgrid(*grid, indexing=indexing, sparse=sparse)
        return grid

    def zeros(self, dtype=float, order=None):
        """Generate an array of zeros matching the object shape.

        Parameters
        ----------
        dtype : np.dtype, optional.
            The dtype of the generated volume
        order : {'F', 'C', None}, optional
            The memory layout order of the generated array. The default is
            ``self.order``.

        Returns
        -------
        y : ndarray
            The generated array of zeros.
        """
        if order is None:
            order = self.order
        z = self.xp.zeros(self.shape, order=self.order, dtype=dtype)
        return z

    def ones(self, dtype=float, order=None):
        """Generate an array of ones matching the object shape.

        Parameters
        ----------
        dtype : np.dtype, optional.
            The dtype of the generated volume
        order : {'F', 'C', None}, optional
            The memory layout order of the generated array. The default is
            ``self.order``.

        Returns
        -------
        y : ndarray
            The generated array of ones.
        """
        if order is None:
            order = self.order
        o = self.xp.ones(self.shape, order=order, dtype=dtype)
        return o

    def unitv(self, loc=None, offset=None, dtype=float, order=None):
        """Unit impulse placed in a volume matching the object's shape.

        Parameters
        ----------
        loc : array-like or None, optional
            Image coordinates for the unit impulse.
        offset : array-like or None, optional
            Image coordinates will be offset by this amount from the center.
        dtype : np.dtype, optional.
            The dtype of the generated volume
        order : {'F', 'C', None}, optional
            The memory layout order of the generated array. The default is
            ``self.order``.

        Returns
        -------
        y : ndarray
            The generated array containing a unit impulse.
        """
        xp = self.xp
        if order is None:
            order = self.order
        ej = xp.zeros(self.shape, dtype=dtype, order=order)

        if loc is None:
            t = xp.floor(xp.asarray(self.shape) / 2)  # "center"
            if offset is not None:
                if len(offset) != len(self.shape):
                    raise ValueError("invalid number of offset dimensions")
                t += offset
            t = tuple(t.astype(int))
        else:
            if len(loc) != len(self.shape):
                raise ValueError("invalid number of loc dimensions")
            t = tuple(int(v) for v in loc)
        ej[t] = 1
        return ej

    def __str__(self):
        str = "{}D ImageGeometry object\n".format(self.ndim)
        str += "shape = {}\n".format(self.shape)
        str += "distances = {}\n".format(self.distances)
        str += "offsets = {}\n".format(self.offsets)
        str += "FOV = {}\n".format(self.fov)
        return str
