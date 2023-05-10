# Third-party imports
import matplotlib.pyplot as plt
import hydra
from omegaconf import DictConfig

# Project imports
import mandelbrot


@hydra.main(version_base=None, config_path="../.", config_name="config")
def run(cfg: DictConfig):

    # Parameters for part of set to display
    iterations = cfg["iterations"]
    width, height = cfg["width"], cfg["height"]
    outdir, outfile = cfg["outdir"], cfg["outfile"]
    format = cfg["format"]
    rmin = cfg["real"]-(1./cfg["zoom"])*cfg["width"]/cfg["height"]
    rmax = cfg["real"]+(1./cfg["zoom"])*cfg["width"]/cfg["height"]
    imin, imax = cfg["imag"]-(1./cfg["zoom"]), cfg["imag"]+(1./cfg["zoom"])
    sigma = cfg["sigma"]
    show = cfg["show"]
    transform = None if cfg["transform"] == "None" else cfg["transform"]
    resample = cfg["resample"]

    # Write to screen
    if cfg["verbose"]:
        print()
        print("Mandelbrot set parameters:")
        print("Minimum and maximum real values:", rmin, rmax)
        print("Minimum and maximum imaginary values:", imin, imax)
        print("Image centre (real, imaginary):", cfg["real"], cfg["imag"])
        print("Image extent (real, imaginary):", rmax-rmin, imax-imin)
        print("Maximum number of iterations:", iterations)
        print("Sigma for Gaussian smoothing [pixels]:", sigma)
        print("Transform:", transform)
        print(f"Width and height of image: {width}, {height}")
        print("Output directory:", outdir)
        print("Output file:", outfile+"."+format)
        print("Printing to screen:", show)
        print("Smooth image:", cfg["smooth"])
        print("Bound image:", cfg["bound"])
        print("Method:", cfg["method"])
        print("Resample factor:", resample)
        print()

    # Display an image on screen and simulatanouesly save it
    data = mandelbrot.create_image(rmin, rmax, imin, imax, iterations, width, height,
                                   smooth_sigma=sigma, transform=transform,
                                   fractional_escape=cfg["smooth"], resample=resample,
                                   calculation_method=cfg["method"],
                                   pad_inches=0., cmap=cfg["cmap"], dpi=224, format=format,
                                   bound_colorbar=cfg["bound"], verbose=True)
    outfile = outdir+"/"+outfile+"."+format
    with open(outfile, "wb") as f:
        f.write(data)
    if show:
        plt.show()
        plt.close()


if __name__ == "__main__":
    run()
