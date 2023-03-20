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


def create_image(real_start, real_end, imag_start, image_end, max_iters, width, height,
                 cmap="cubehelix", figsize=(6, 6), dpi=224, sigma=1.):
    """
    Create a png and return it as a binary
    """
    array = sample_area(real_start, real_end, imag_start,
                        image_end, max_iters, width, height)
    if sigma != 0.:
        array = gaussian_filter(array, sigma=sigma)
    plt.subplots(figsize=figsize, dpi=dpi, frameon=False)
    plt.imshow(array, cmap=cmap, vmin=0., vmax=max_iters)
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight',
                pad_inches=0)      # Place the png as a binary in memory
    data = buffer.getvalue()       # Get the binary
    data = base64.b64encode(data)  # Encode to base64 bytes
    data = data.decode()           # Convert bytes to string
    return data  # Return the encoded png binary
