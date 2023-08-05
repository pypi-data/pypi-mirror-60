import numpy as np
import pytest

from mrrt.utils import ImageGeometry, ellipse_im
from mrrt import utils

array_modules = [np]
if utils.config.have_cupy:
    import cupy

    array_modules += [cupy]


def test_image_geom():
    # list/scalar distances
    ig = ImageGeometry(shape=[5, 5], distances=1)
    assert ig.distances == (1, 1)
    ig = ImageGeometry(shape=[5, 5], distances=[1, 1])
    assert ig.distances == (1, 1)
    ig = ImageGeometry(shape=[5, 5], fov=(5, 5))
    assert ig.distances == (1, 1)

    z = ig.zeros()
    assert z.shape == ig.shape
    assert z.sum() == 0

    o = ig.ones()
    assert o.shape == ig.shape
    assert np.all(o == 1)

    u = ig.unitv()
    assert u[2, 2] == 1
    assert u.sum() == 1

    u = ig.unitv(offset=(1, -1))
    assert u[3, 1] == 1
    assert u.sum() == 1

    u = ig.unitv(loc=(2, 4))
    assert u[2, 4] == 1
    assert u.sum() == 1

    print(ig)


@pytest.mark.parametrize("xp", array_modules)
def test_image_geom_mask(xp):
    mask = xp.zeros((3, 3), dtype=xp.bool)
    mask[1, :] = 1
    mask[:, 1] = 1
    ig = ImageGeometry(shape=mask.shape, distances=1, mask=mask, xp=xp)
    assert ig.nmask == mask.sum()

    x = xp.arange(mask.size).reshape(mask.shape)
    xm_expected = x * mask
    y = ig.masker(x)
    xm = ig.embed(y)
    xp.testing.assert_allclose(xm_expected, xm)

    # non-boolean mask
    maskf = mask.astype(float)
    with pytest.raises(ValueError):
        ImageGeometry(shape=mask.shape, distances=1, mask=maskf, xp=xp)


def test_image_geom_grids():
    # list/scalar distances
    ig = ImageGeometry(shape=[5, 7], distances=2)
    sx, sy = ig.grid()
    assert sx.size == ig.shape[0]
    assert sy.size == ig.shape[1]
    assert sx.ndim == sy.ndim == 2
    assert np.squeeze(sx)[0] == -ig.shape[0] / 2 * ig.distances[0]
    assert np.squeeze(sy)[0] == -ig.shape[1] / 2 * ig.distances[1]

    sxd, syd = ig.grid(sparse=False)
    assert sxd.shape == ig.shape
    assert syd.shape == ig.shape

    fx, fy = ig.fgrid()
    assert fx.size == ig.shape[0]
    assert fy.size == ig.shape[1]
    assert fx.ndim == fy.ndim == 2
    fxd, fyd = ig.fgrid(sparse=False)
    assert fxd.shape == ig.shape
    assert fyd.shape == ig.shape


def test_ellipse_im(show_fig=False):
    """Basic test: only verifies that the phantoms have the expected shape."""
    ig = ImageGeometry(shape=(2 ** 8, 2 ** 8 + 2), fov=250)
    x0, params = ellipse_im(ig, "shepplogan", oversample=2)
    assert x0.shape == ig.shape
    x1, params = ellipse_im(ig, "shepplogan-emis", oversample=2)
    assert x1.shape == ig.shape
    x2, params = ellipse_im(ig, "shepplogan-mod", oversample=2)
    assert x2.shape == ig.shape
