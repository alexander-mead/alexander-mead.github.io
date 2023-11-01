# Standard imports
import io
import math

# Third-part imports
import numpy as np
from scipy.stats import beta as beta_dist
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from numba import njit, prange

# Project imports
# from .Fortran import mandelbrot # Works with FastAPI server
from Fortran import mandelbrot  # Works with python image.py


def sample_area_python(real_start: float, real_end: float, imag_start: float, imag_end: float,
                       max_iters: int, width: int, height: int, smooth=False) -> np.array:
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
                if abs(z) > 2.:  # Divergence # TODO: Test abs vs. np.abs
                    if smooth:  # Fractional iteration count
                        n = i + 1. - \
                            math.log(math.log(abs(z)))/math.log(2.)
                    else:
                        n = i
                    break
            m[irow, icol] = n
    return m


@njit(parallel=True)
def sample_area_numba(real_start: float, real_end: float, imag_start: float, imag_end: float,
                      max_iters: int, width: int, height: int, smooth=False) -> np.array:
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
                if abs(z) > 2.:  # Divergence # TODO: Test abs vs. np.abs
                    if smooth:  # Fractional iteration count
                        n = i + 1. - \
                            np.log(np.log(np.abs(z)))/np.log(2.)
                    else:
                        n = i
                    break
            m[irow, icol] = n
    return m


def sample_area_numpy(real_start: float, real_end: float, imag_start: float, imag_end: float,
                      max_iters: int, width: int, height: int, smooth=False) -> np.array:
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


def warp_image(image_array: np.array, alpha=1., beta=1.) -> np.array:
    """
    Takes an image defined on 0 to 1 and returns a uniform image
    Pixel values are scaled so that the distribution is approximately uniform
    Thanks chatGPT for this function
    """
    # Flatten the image array and sort the pixel intensities
    sorted_pixel_values = np.unique(np.sort(image_array.flatten()))

    # Calculate the cumulative distribution function (CDF) of the pixel intensities
    histogram, _ = np.histogram(image_array, bins=len(
        sorted_pixel_values), range=(0, 1))
    cdf = np.cumsum(histogram)
    cdf_normalized = cdf / cdf[-1]  # Normalize the CDF to the range [0, 1]

    # Create the desired beta distribution with shape parameters alpha and beta
    x = np.linspace(0, 1, len(sorted_pixel_values))
    target_cdf = beta_dist.cdf(x, alpha, beta)

    # Map the normalized CDF values to the target beta distribution's inverse CDF values
    new_pixel_values = np.interp(cdf_normalized, target_cdf, x)

    # Use interpolation to map the original pixel values to the new pixel values
    image_array_centralized = np.interp(
        image_array, sorted_pixel_values, new_pixel_values)

    return image_array_centralized


def transform_image(array: np.array, transform: str | float) -> np.array:
    """
    Apply a transform to the image, initial pixel values are between 0 and 1
    Final pixel values should also be between 0 and 1
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
    elif transform == "inverse":
        array[array == 0.] = 1.
        array = (1./(1.+array)-0.5)/0.5
    elif transform == "uniform":
        array = warp_image(array, alpha=1., beta=1.)
    elif transform == "centralize_low":
        array = warp_image(array, alpha=2., beta=2.)
    elif transform == "centralize_med":
        array = warp_image(array, alpha=5., beta=5.)
    elif transform == "centralize_high":
        array = warp_image(array, alpha=10., beta=10.)
    else:
        raise ValueError("Transform not recognised")
    return array


def create_image(real_start: float, real_end: float, imag_start: float, imag_end: float,
                 max_iters: int, width: int, height: int,
                 smooth_sigma=0.5, transform=None, fractional_escape=True, resample=1,
                 calculation_method="Fortran",
                 pad_inches=0., cmap="cubehelix", dpi=224, format="png",
                 bound_colorbar=True, verbose=False) -> bytes:
    """
    Create a png and return it as a binary
    """

    # Sample the area
    _width, _height = width*resample, height*resample
    if calculation_method == "python":
        array = sample_area_python(real_start, real_end, imag_start,
                                   imag_end, max_iters, _width, _height,
                                   fractional_escape)
    elif calculation_method == "numpy":
        array = sample_area_numpy(real_start, real_end, imag_start,
                                  imag_end, max_iters, _width, _height,
                                  fractional_escape)
    elif calculation_method == "Fortran":
        array = mandelbrot.sample_area(real_start, real_end, imag_start,
                                       imag_end, max_iters, _width, _height,
                                       fractional_escape)
        array = array.T
    elif calculation_method == "numba":
        array = sample_area_numba(real_start, real_end, imag_start,
                                  imag_end, max_iters, _width, _height,
                                  fractional_escape)
    else:
        raise ValueError("Method not recognised")

    # Process image
    if verbose:
        print(f"Min/max pre-shrink; pre-smooth: {array.min(), array.max()}")
    array = array/(max_iters-1)
    if fractional_escape:  # Here, it possible for values to be greater than 1
        array[array > 1.] = 1.
    if verbose:
        print(f"Min/max post-shrink; pre-smooth: {array.min(), array.max()}")
    if smooth_sigma != 0.:
        array = gaussian_filter(array, sigma=smooth_sigma)
    if verbose:
        print(f"Min/max post-shrink; post-smooth: {array.min(), array.max()}")
    array = transform_image(array, transform)
    if resample > 1:  # Average image pixels over resample x resample grid
        array = array.reshape(height, resample, width,
                              resample).mean(axis=(1, 3))

    # Plot
    figsize = width/dpi, height/dpi
    plt.subplots(figsize=figsize, dpi=dpi, frameon=False)
    vmin, vmax = (0., 1.) if bound_colorbar else (None, None)
    plt.imshow(array, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, bbox_inches='tight', format=format,
                pad_inches=pad_inches)  # Place the image as a binary in memory
    buffer = buffer.getvalue()
    return buffer  # Return the image binary (avoids saving to disk)
