# import pytest
import numpy as np
from mrrt.utils import hist_equal

rseed = 0


def test_hist_equal_2d(show_figure=False):
    nhist = 1000
    rstate = np.random.RandomState(rseed)
    r1 = 10 * rstate.randn(nhist)
    r2 = 40 + 10 * rstate.randn(nhist)
    i1 = 5 * rstate.randn(nhist)
    i2 = 7 + 3 * rstate.randn(nhist)
    x = np.concatenate((r1 + 1j * i1, r2 + 1j * i2))
    x = np.stack((x.real, 1 + 1 * x.imag), axis=1)
    ncent = (18, 15)
    nk, cents = hist_equal(x, ncent, ifsame="1bin")

    assert nk.shape == ncent
    assert cents[0].size == ncent[0]
    assert cents[1].size == ncent[1]

    if show_figure:
        from matplotlib import pyplot as plt

        fig = plt.figure()
        ax1 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
        ax2 = plt.subplot2grid((1, 2), (0, 1), colspan=1, rowspan=1)

        ax1.plot(x[:, 0], x[:, 1], ".")
        creal = cents[0]
        cimag = cents[1]
        creal, cimag = np.meshgrid(creal, cimag, indexing="ij")
        ax1.plot(creal.ravel(), cimag.ravel(), "g.")

        # ax2=plt.subplot(122)
        xmin = np.min(cents[0])
        xmax = np.max(cents[0])
        ymin = np.min(cents[1])
        ymax = np.max(cents[1])
        ax2.imshow(
            nk.T,
            interpolation="nearest",
            cmap=plt.cm.gray,
            extent=(xmin, xmax, ymin, ymax),
            origin="lower",
            aspect="auto",
        )
        fig.show()
    return


def test_hist_equal_3d():
    rstate = np.random.RandomState(rseed)
    nhist = 1000
    x1 = 10 * rstate.randn(nhist)
    x2 = 40 + 8 * rstate.randn(nhist)
    x3 = 25 + 4 * rstate.randn(nhist)
    y1 = -10 + 10 * rstate.randn(nhist)
    y2 = 7 + 3 * rstate.randn(nhist)
    y3 = 0 - 2.5 * rstate.randn(nhist)
    z1 = -4 + 6 * rstate.randn(nhist)
    z2 = 7 + 3 * rstate.randn(nhist)
    z3 = 0 - 3 * rstate.randn(nhist)
    x = np.concatenate((x1, x2, x3))  # 2000x1
    y = np.concatenate((y1, y2, y3))  # 2000x1
    z = np.concatenate((z1, z2, z3))
    data = np.stack((x, y, z), axis=1)  # 2000x2
    ncent = (28, 35, 33)
    nk, cents = hist_equal(data, ncent)
    assert nk.shape == ncent
    assert cents[0].size == ncent[0]
    assert cents[1].size == ncent[1]
    assert cents[2].size == ncent[2]

    return
