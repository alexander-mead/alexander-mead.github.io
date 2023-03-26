import io
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import base64


def sample_area(real_start, real_end, imag_start, image_end, max_iters, width, height):
    """
    Loops over an area and assigns points to the Mandelbrot set
    Thanks chatGPT for this vectorized version (although it was wrong to begin with)
    """
    x, y = np.meshgrid(np.linspace(real_start, real_end, width),
                       np.linspace(imag_start, image_end, height))
    mandelbrot_set = np.zeros((height, width))
    c = x + y * 1j        # Map x, y to their complex values
    z = np.zeros_like(c)  # Initialise the value of 'z' at each location
    for i in range(max_iters):
        z = z**2 + c               # Iterate
        mask = np.abs(z) > 2.      # Select points that are diverging
        mandelbrot_set[mask] = i   # Set is number of iterations for divergence
        z[mask], c[mask] = 0., 0.  # Reset the diverging point so that it will not diverge in future
    return mandelbrot_set


def transform_image(array, transform):
    """
    Apply a transform to the image
    """
    if transform is None:
        pass
    elif transform == "log":
        array = np.log(1.+array)/np.log(2.)
    elif transform == "square_root":
        array = np.sqrt(array)
    elif transform == "cube_root":
        array = np.cbrt(array)
    elif type(transform) is float:
        array = array**transform
    else:
        raise ValueError("Transform not recognised")
    return array


def create_image(real_start, real_end, imag_start, imag_end, max_iters, width, height,
                 sigma=0.5, transform=None,
                 cmap="cubehelix", dpi=224, format="png"):
    """
    Create a png and return it as a binary
    """
    array = sample_area(real_start, real_end, imag_start,
                        imag_end, max_iters, width, height)
    array /= max_iters-1  # Normalise
    if sigma != 0.:
        array = gaussian_filter(array, sigma=sigma)
    array = transform_image(array, transform)
    figsize = width/dpi, height/dpi
    plt.subplots(figsize=figsize, dpi=dpi, frameon=False)
    plt.imshow(array, cmap=cmap, vmin=0., vmax=1.)  # , vmax=max(array))
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, bbox_inches='tight', format=format,
                pad_inches=0)  # Place the image as a binary in memory
    buffer = buffer.getvalue()
    return buffer   # Return the image binary (avoids saving to disk)
