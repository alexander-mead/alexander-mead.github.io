# Standard imports
import io
import math

# Third-part imports
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from numba import njit, prange

# Project imports
from Fortran import mandelbrot


def sample_area_python(real_start, real_end, imag_start, imag_end, max_iters, width, height, smooth=False):
    """
    Loops over an area and assigns points to the Mandelbrot set
    Thanks chatGPT for this vectorized version (although it was wrong to begin with)
    """
    m = np.zeros((height, width))
    for irow in range(height):
        for icol in range(width):
            x = real_start + (real_end - real_start) * icol / width
            y = imag_end + (imag_start - imag_end) * irow / height
            z = 0.
            c = x + y * 1j
            n = 0
            for i in range(max_iters):
                z = z**2 + c
                if np.abs(z) > 2.:  # Divergence
                    if smooth:  # Fractional iteration count
                        n = i + 1. - \
                            math.log(math.log(abs(z)))/math.log(2.)
                    else:
                        n = i
                    break
            m[irow, icol] = n
    return m


@njit(parallel=True)
def sample_area_numba(real_start, real_end, imag_start, imag_end, max_iters, width, height, smooth=False):
    """
    Loops over an area and assigns points to the Mandelbrot set
    Thanks chatGPT for this vectorized version (although it was wrong to begin with)
    """
    m = np.zeros((height, width))
    for irow in prange(height):
        for icol in prange(width):
            x = real_start + (real_end - real_start) * icol / width
            y = imag_end + (imag_start - imag_end) * irow / height
            z = 0.
            c = x + y * 1j
            n = 0
            for i in range(max_iters):
                z = z**2 + c
                if np.abs(z) > 2.:  # Divergence
                    if smooth:  # Fractional iteration count
                        n = i + 1. - \
                            np.log(np.log(np.abs(z)))/np.log(2.)
                    else:
                        n = i
                    break
            m[irow, icol] = n
    return m


def sample_area_numpy(real_start, real_end, imag_start, imag_end, max_iters, width, height, smooth=False):
    """
    Loops over an area and assigns points to the Mandelbrot set
    Thanks chatGPT for this vectorized version (although it was wrong to begin with)
    """
    x, y = np.meshgrid(np.linspace(real_start, real_end, width),
                       np.linspace(imag_end, imag_start, height))
    mandelbrot_set = np.zeros((height, width))
    c = x + y * 1j        # Map x, y to their complex values
    z = np.zeros_like(c)  # Initialise the value of 'z' at each location
    for i in range(max_iters):
        z = z**2 + c               # Iterate
        mask = np.abs(z) > 2.      # Select points that are diverging
        if smooth:  # Fractional iteration count
            mandelbrot_set[mask] = i + 1. - \
                np.log(np.log(np.abs(z[mask])))/np.log(2.)
        else:  # Set is number of iterations for divergence
            mandelbrot_set[mask] = i
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
                 cmap="cubehelix", dpi=224, format="png",
                 smooth=True, bound=True, method="Fortran"):
    """
    Create a png and return it as a binary
    """

    if method == "Fortran":
        array = mandelbrot.sample_area(real_start, real_end, imag_start,
                                       imag_end, max_iters, width, height,
                                       smooth)
        array = array.T
    elif method == "python":
        array = sample_area_python(real_start, real_end, imag_start,
                                   imag_end, max_iters, width, height,
                                   smooth)
    elif method == "numpy":
        array = sample_area_numpy(real_start, real_end, imag_start,
                                  imag_end, max_iters, width, height,
                                  smooth)
    elif method == "numba":
        array = sample_area_numba(real_start, real_end, imag_start,
                                  imag_end, max_iters, width, height,
                                  smooth)
    else:
        raise ValueError("Method not recognised")
    array = array/(max_iters-1)
    if sigma != 0.:
        array = gaussian_filter(array, sigma=sigma)
    array = transform_image(array, transform)
    figsize = width/dpi, height/dpi
    plt.subplots(figsize=figsize, dpi=dpi, frameon=False)
    vmin, vmax = (0., 1.) if bound else (None, None)
    plt.imshow(array, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, bbox_inches='tight', format=format,
                pad_inches=0)  # Place the image as a binary in memory
    buffer = buffer.getvalue()
    return buffer   # Return the image binary (avoids saving to disk)
