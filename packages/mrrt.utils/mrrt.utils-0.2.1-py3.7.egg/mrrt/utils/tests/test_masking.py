import numpy as np
from numpy import testing
import pytest

from mrrt.utils import embed, masker, have_cupy, ArrayMasker

all_xp = [np]
if have_cupy:
    import cupy

    all_xp += [cupy]

# TODO: remove old masker, embed


@pytest.mark.parametrize("xp", all_xp)
def test_masker_shape(xp):
    rstate = xp.random.RandomState(5)
    shape = (32, 16)
    x = xp.arange(np.prod(shape)).reshape(shape)
    x5e = xp.stack((x,) * 5, axis=-1)
    x5b = xp.stack((x,) * 5, axis=0)
    mask = rstate.standard_normal(shape) > 0
    nmask = mask.sum()
    if xp != np:
        nmask = nmask.get()

    Mend = ArrayMasker(mask, mask_first_axes=True)
    Mbeg = ArrayMasker(mask, mask_first_axes=False)

    vals1 = Mend.masker(x5e)
    with pytest.raises(ValueError):
        Mend.masker(x5b)
    assert vals1.shape[-1] == x5e.shape[-1]
    assert vals1.shape[0] == nmask
    assert vals1.ndim == x5e.ndim - mask.ndim + 1

    vals2 = Mbeg.masker(x5b)
    with pytest.raises(ValueError):
        Mbeg.masker(x5e)
    assert vals2.shape[0] == x5b.shape[0]
    assert vals2.shape[-1] == nmask
    assert vals2.ndim == x5b.ndim - mask.ndim + 1


@pytest.mark.parametrize("xp", all_xp)
def test_masker_values(xp):
    rstate = xp.random.RandomState(5)
    shape = (16, 8)
    x = xp.arange(np.prod(shape)).reshape(shape)
    x5e = xp.stack((x,) * 5, axis=-1)
    x5b = xp.stack((x,) * 5, axis=0)
    mask = rstate.standard_normal(shape) > 0
    nmask = mask.sum()
    if xp != np:
        nmask = nmask.get()

    Mend = ArrayMasker(mask, mask_first_axes=True)
    Mbeg = ArrayMasker(mask, mask_first_axes=False)

    # Same masked values are returned in all cases, but not necessarily in
    # the same order.
    # To test, sort the raveled values after masking to do the comparisons
    vals1 = xp.sort(Mend.masker(x5e).ravel())
    xp.testing.assert_array_equal(vals1, xp.sort(Mbeg.masker(x5b).ravel()))
    x5e = xp.asfortranarray(x5e)
    x5b = xp.asfortranarray(x5b)
    xp.testing.assert_array_equal(vals1, xp.sort(Mend.masker(x5e).ravel()))
    xp.testing.assert_array_equal(vals1, xp.sort(Mbeg.masker(x5b).ravel()))


@pytest.mark.parametrize("xp", all_xp)
def test_mask_and_embed(xp):
    rstate = xp.random.RandomState(5)
    shape = (16, 8)
    x = xp.arange(np.prod(shape)).reshape(shape)
    x5e = xp.stack((x,) * 5, axis=-1)
    x5b = xp.stack((x,) * 5, axis=0)
    mask = rstate.standard_normal(shape) > 0
    nmask = mask.sum()
    if xp != np:
        nmask = nmask.get()

    Mend = ArrayMasker(mask, mask_first_axes=True)
    Mbeg = ArrayMasker(mask, mask_first_axes=False)

    expected_e = x5e * mask[..., np.newaxis]
    expected_b = x5b * mask[np.newaxis, ...]

    assert xp.all(Mend.embed(Mend.masker(x5e)) == expected_e)
    assert xp.all(Mbeg.embed(Mbeg.masker(x5b)) == expected_b)

    x5e = xp.asfortranarray(x5e)
    x5b = xp.asfortranarray(x5b)
    assert xp.all(Mend.embed(Mend.masker(x5e)) == expected_e)
    assert xp.all(Mbeg.embed(Mbeg.masker(x5b)) == expected_b)


@pytest.mark.parametrize("xp", all_xp)
def test_mask_and_embed_two_extra_axes(xp):
    rstate = xp.random.RandomState(5)
    shape = (16, 8)
    x = xp.arange(np.prod(shape)).reshape(shape)
    xe = xp.stack((x,) * 5, axis=-1)
    xe = xp.stack((xe,) * 2, axis=-1)
    xb = xp.stack((x,) * 5, axis=0)
    xb = xp.stack((xb,) * 2, axis=0)
    mask = rstate.standard_normal(shape) > 0
    nmask = mask.sum()
    if xp != np:
        nmask = nmask.get()

    Mend = ArrayMasker(mask, mask_first_axes=True)
    Mbeg = ArrayMasker(mask, mask_first_axes=False)

    expected_e = xe * mask[..., np.newaxis, np.newaxis]
    expected_b = xb * mask[np.newaxis, np.newaxis, ...]

    assert xp.all(Mend.embed(Mend.masker(xe)) == expected_e)
    assert xp.all(Mbeg.embed(Mbeg.masker(xb)) == expected_b)

    xe = xp.asfortranarray(xe)
    xb = xp.asfortranarray(xb)
    assert xp.all(Mend.embed(Mend.masker(xe)) == expected_e)
    assert xp.all(Mbeg.embed(Mbeg.masker(xb)) == expected_b)


mask = np.asarray([[1, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]], dtype=np.bool)
arr = np.asarray([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]], dtype=np.float32)
nmask = mask.sum()


def test_masker():
    am = masker(arr, mask, order="F", squeeze_output=True)
    testing.assert_array_almost_equal(am, [0, 8, 1, 7])
    assert am.shape == (nmask,)
    expected_embed = arr * mask
    testing.assert_array_equal(expected_embed, embed(am, mask, order="F"))

    # am = masker(arr, mask, order="C", squeeze_output=True)
    # testing.assert_array_almost_equal(am, [0, 1, 7, 8])
    # assert am.shape == (nmask,)
    # testing.assert_array_equal(expected_embed, embed(am, mask, order="C"))

    am = masker(arr, mask, order="F", squeeze_output=False)
    testing.assert_array_almost_equal(am[:, 0], [0, 8, 1, 7])
    assert am.shape == (nmask, 1)
    testing.assert_array_equal(expected_embed, embed(am, mask, order="F"))


def test_masker_multidim():
    nreps = 8
    arr3 = np.tile(arr[..., np.newaxis], (1, 1, nreps))
    am3 = masker(arr3, mask, order="F")
    assert am3.shape == (nmask, nreps)
    testing.assert_array_almost_equal(am3[:, 0], [0, 8, 1, 7])
    expected_embed = arr3 * mask[..., np.newaxis]
    testing.assert_array_almost_equal(
        expected_embed, embed(am3, mask, order="F")
    )

    # am3 = masker(arr3, mask, order="C")
    # assert am3.shape == (nmask, nreps)
    # testing.assert_array_almost_equal(am3[:, 0], [0, 1, 7, 8])
    # testing.assert_array_almost_equal(
    #     expected_embed, embed(am3, mask, order="C")
    # )

    # repetitions at start is not supported
    # arr3_v2 = np.tile(arr[np.newaxis, ...], (nreps, 1, 1))
    # testing.assert_raises(ValueError, masker, arr3_v2, mask, order="C")


# def test_masker_multidim2():
#     nreps1 = 4
#     nreps2 = 2
#     arr4 = np.tile(arr[..., np.newaxis, np.newaxis], (1, 1, nreps1, nreps2))
#     am4 = masker(arr4, mask, order="F", prod_dim=True)
#     assert am4.shape == (nmask, nreps1 * nreps2)

#     am4 = masker(arr4, mask, order="C", prod_dim=True)
#     assert am4.shape == (nmask, nreps1 * nreps2)

#     am4 = masker(arr4, mask, order="F", prod_dim=False)
#     assert am4.shape == (nmask, nreps1, nreps2)

#     am4 = masker(arr4, mask, order="C", prod_dim=False)
#     assert am4.shape == (nmask, nreps1, nreps2)


def test_masker_simple():
    mask = np.zeros((3, 2), dtype=np.bool)
    mask[0, 1] = 1
    mask[2, 0] = 1
    x = np.arange(6).reshape((3, 2))
    testing.assert_array_equal(masker(x, mask, order="F"), np.array([4, 1]))
    # testing.assert_array_equal(masker(x, mask, order="C"), np.array([1, 4]))

    # testing.assert_array_equal(masker(x, mask, order="C"), x[mask])

    x3 = np.arange(12).reshape((3, 2, 2))
    testing.assert_array_equal(
        masker(x3, mask, order="F"), np.array([[8, 9], [2, 3]])
    )


#    testing.assert_array_equal(masker(x3, mask, order="C"), x3[mask])


def test_embed_demo(show_figure=False):
    shape = (512, 500)
    mask = np.ones(shape, dtype=np.bool)
    mask[:8, :8] = 0

    x = np.arange(mask.sum())
    y1 = embed(x, mask)

    y2 = embed(np.column_stack((x, x, x, x)), mask)

    np.testing.assert_allclose(y1, y2[:, :, 1])

    if show_figure:
        import matplotlib.pyplot as plt

        plt.figure(), plt.imshow(y1.T), plt.show()

    x3 = np.tile(x[:, None, None], (1, 2, 3))
    y3 = embed(x3, mask)
    assert y3.ndim == mask.ndim + x3.ndim - 1

    np.testing.assert_allclose(y1, y3[:, :, -1, -1])
