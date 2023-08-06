from matplotlib import pyplot as plt

from mrrt.utils import ImageGeometry, ellipse_im

ig = ImageGeometry(shape=(2 ** 8, 2 ** 8 + 2), fov=250)

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for i, name in enumerate(["shepplogan", "shepplogan-emis", "shepplogan-mod"]):
    phantom, params = ellipse_im(ig, name, oversample=2)
    im = axes[i].imshow(
        phantom.T,
        interpolation="nearest",
        cmap=plt.cm.gray,  # vmin=0.9, vmax=1.1
    )
    axes[i].set_title(name)
    axes[i].set_axis_off()
    fig.colorbar(
        im, ax=axes[i], orientation="vertical", fraction=0.1, shrink=0.9
    )

plt.tight_layout()
plt.show()
