# Standard imports
import io

# Third-party imports
import numpy as np
from scipy.optimize import fsolve
from scipy.integrate import quad
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import camb
import hmcode
# from numba import njit, prange

digilab_colors = [
    "#162448",  # Dark blue
    "#009FE3",  # Light blue
    "#7DB928",  # Green
    "#EEEEEE",  # Cement
]
digilab_cmap = LinearSegmentedColormap.from_list("", digilab_colors)
# kfac_trunc = np.pi/2.
kfac_trunc = 1.


def Pk_interp(k: np.array, Pk: np.array) -> callable:
    """
    Careful, this function returns a function, which is thought prevoking
    This can interpolate both 3D and 2D power spectra
    """
    interpolator = interp1d(np.log(k), np.log(Pk),
                            kind='linear',
                            assume_sorted=True,
                            bounds_error=False,
                            fill_value='extrapolate',  # Only works with linear
                            )
    return lambda x: np.exp(interpolator(np.log(x)))


def make_Gaussian_random_field_2D(mean_value: float, power_spectrum: callable,
                                  map_size: int, mesh_cells: int) -> np.ndarray:
    """
    Parameters:
        mean_value: mean value for the field
        power_spectrum: P(k, *args) power spectrum for the field [(length units)^2]
        map_size: side length for the map [length units]
        mesh_cells: number of mesh cells for the field
    """

    # TODO: Enforce Hermitian condition
    # TODO: Use real-to-real FFT
    # TODO: Generalise to nD

    cfield = np.zeros((mesh_cells, mesh_cells), dtype=complex)
    mesh_size = map_size/mesh_cells
    cfield = np.zeros((mesh_cells, mesh_cells), dtype=complex)

    # Look-up arrays for the wavenumbers
    # 2pi needed to convert frequency to angular frequency
    kx = np.fft.fftfreq(mesh_cells, d=mesh_size)*2.*np.pi
    ky = kx  # k in the y direction are identical to those in the x direction

    # Fill the map in Fourier space
    k_grid = np.sqrt(kx**2+ky[:, None]**2)
    k_grid[0, 0] = 1e-10  # Avoid division by zero
    sigma_grid = np.sqrt(power_spectrum(k_grid))/map_size
    x, y = np.random.normal(0., sigma_grid, size=(2, mesh_cells, mesh_cells))
    cfield = x + 1j*y
    cfield[0, 0] = mean_value

    # FFT
    cfield = np.fft.ifft2(cfield)
    cfield = cfield*mesh_cells**2  # Normalisation

    # Convert to real
    # For non-periodic arrays we discard some
    field = np.real(cfield[0:mesh_cells, 0:mesh_cells])
    return field


def Dk2D(k: np.array, Pk: callable) -> np.array:
    Dk = 2.*np.pi*((k/(2.*np.pi))**2)*Pk(k)
    return Dk


def Dk3D(k: np.array, Pk: callable) -> np.array:
    Dk = 4.*np.pi*((k/(2.*np.pi))**3)*Pk(k)
    return Dk


def Dk2D_integrand(x: float, k: np.array, Pk: callable, T: float) -> float:
    Wk = np.sinc(T*x)
    Dk = Dk3D(np.sqrt(x**2+k**2), Pk)
    integrand = Dk*Wk**2/np.sqrt(x**2+k**2)**3
    return integrand


# @njit(parallel=True)
def get_Pk2D(k: np.array, Pk: callable, T: float) -> np.array:
    Dk = []
    for _k in k:
        _Dk, _ = quad(Dk2D_integrand, 0., np.inf, args=(
            _k, Pk, T), limit=100, epsabs=0., epsrel=1e-3)  # Note that max error is used as target
        Dk.append(_Dk)
    Dk = (k**2)*np.array(Dk)
    Pk = Dk/(2.*np.pi*(k/(2.*np.pi))**2)
    return Pk


def get_Pk3D(params: dict, k: np.array, z, norm_sigma8=True, verbose=False) -> bytes:

    # Constants
    kfac_CAMB = 10.  # How much bigger is CAMB kmax
    As = 2e-9 if norm_sigma8 else params['A_s']
    zs = [z]  # Redshifts

    # Initial run of CAMB
    pars = camb.CAMBparams(WantCls=False)
    Omega_c = params['Omega_m']-params['Omega_b']
    omega_c = Omega_c*(params['H_0']/100.)**2
    omega_b = params['Omega_b']*(params['H_0']/100.)**2
    pars.set_cosmology(omch2=omega_c, ombh2=omega_b,
                       H0=params['H_0'], mnu=params['m_nu'])
    pars.set_dark_energy(
        w=params['w_0'], wa=params['w_a'], dark_energy_model='ppf')
    pars.InitPower.set_params(As=As, ns=params['n_s'])
    pars.set_matter_power(redshifts=zs, kmax=kfac_CAMB*kmax)

    # Scale 'As' to be correct for the desired 'sigma_8' value if necessary
    if norm_sigma8:
        results = camb.get_results(pars)
        sigma_8_init = results.get_sigma8_0()
        scaling = (params['sigma_8']/sigma_8_init)**2
        As *= scaling
        pars.InitPower.set_params(As=As, ns=params['n_s'])

    # Run CAMB
    results = camb.get_results(pars)
    if verbose:
        sigma_8 = results.get_sigma8_0()
        print('sigma_8:', sigma_8)

    # HMcode
    Pk = hmcode.power(k, zs, results)[zs.index(z)]
    return Pk


def smooth_nonlinear_power(k: np.array, Pk: np.array, T=None, verbose=False):
    """
    Calculate kmax_Pk from the power spectrum
    Defined as a non-linear wavenumber where D^2(k_max)=1.
    """
    k_initial_guess = 0.1
    if T is None:  # Use the 3D power spectrum here...
        kmax_Pk = fsolve(lambda x: Dk3D(x, Pk_interp(k, Pk))-1.,
                         k_initial_guess)[0]
    else:  # ...otherwise use the 2D one
        kmax_Pk = fsolve(lambda x: Dk2D(x, Pk_interp(k, Pk))-1.,
                         k_initial_guess)[0]
    kmax_Pk *= kfac_trunc
    if verbose:
        print(f"Truncation k: {kmax_Pk} h/Mpc")
    Pk *= np.exp(-k/kmax_Pk)
    return Pk


def lognormal_transform(delta, verbose=False):
    """
    Log-normal transform of field with renormalisation
    """
    delta = np.exp(delta)-1.
    delta = -1.+(1.+delta)/(1.+delta.mean())
    if verbose:
        print(f"Minimum and maximum field values: {delta.min(), delta.max()}")
        print(f"Mean and standard deviation: {delta.mean(), delta.std()}")
        print()
    return delta


def make_image(params: dict, krange=(1e-3, 1e2), nk=128, z=0., L=500., T=None, n=512,
               vrange=(None, None), box_h_units=True, truncate_Pk=True,
               log_normal_transform=True, plot_log_overdensity=True,
               norm_sigma8=True,
               smooth_sigma=0.5, pad_inches=0., cmap=digilab_cmap,
               figsize=(8, 8),
               verbose=False) -> bytes:

    # Ranges
    kmin, kmax = krange
    k = np.logspace(np.log10(kmin), np.log10(kmax), nk)

    # Power spectrum
    Pk_3D = get_Pk3D(params, k, z, norm_sigma8=norm_sigma8, verbose=verbose)
    if T is not None:
        Pk = get_Pk2D(k, Pk_interp(k, Pk_3D), T)
    else:
        Pk = Pk_3D

    # Truncate power spectrum
    if truncate_Pk:
        Pk = smooth_nonlinear_power(k, Pk, T=T, verbose=verbose)

    # Generate Gaussian random field
    # TODO: Check the length transformation L -> L/h or L -> L*h ?!?
    L_here = L if box_h_units else L/(params['H_0']/100.)
    delta = make_Gaussian_random_field_2D(0., Pk_interp(k, Pk), L_here, n)

    if log_normal_transform:
        delta = lognormal_transform(delta, verbose=verbose)

    # Smooth image
    if smooth_sigma != 0.:
        delta = gaussian_filter(delta, sigma=smooth_sigma)

    # Plot
    plt.subplots(figsize=figsize, dpi=224)
    vmin, vmax = vrange
    if plot_log_overdensity:
        eps = 1.+delta[delta > -1.].min()
        vmin_here = np.log10(vmin) if vmin is not None else None
        vmax_here = np.log10(vmax) if vmax is not None else None
        plt.imshow(np.log10(1.+delta+eps), vmin=vmin_here,
                   vmax=vmax_here, cmap=cmap)
    else:
        plt.imshow(1.+delta, vmin=vmin, vmax=vmax, cmap=cmap)
    plt.xticks([])
    plt.yticks([])
    buffer = io.BytesIO()
    plt.savefig(buffer, bbox_inches='tight',
                format='png', pad_inches=pad_inches)
    buffer = buffer.getvalue()
    return buffer  # Return the image binary


if __name__ == "__main__":

    params = {
        'Omega_m': 0.3,
        'Omega_b': 0.045,
        'H_0': 70.,
        'w_0': -1.,
        'w_a': 0.,
        'sigma_8': 0.8,
        'A_s': 2.1e-9,
        'n_s': 0.96,
        'm_nu': 0.,
    }
    kmin, kmax = 1e-3, 1e2
    nk = 128
    z = 0.
    L = 500.
    T = 1.
    n = 512
    seed = 123
    truncate_Pk = True
    plot_log_overdensity = False
    if plot_log_overdensity:
        vmin, vmax = 1e-1, 10.
    else:
        vmin, vmax = 0., 15.
    # vmin, vmax = None, None
    # cmap = 'cubehelix'
    cmap = digilab_cmap

    np.random.seed(seed)

    _ = make_image(params, (kmin, kmax), nk, z, L, T, n,
                   vrange=(vmin, vmax),
                   truncate_Pk=truncate_Pk,
                   plot_log_overdensity=plot_log_overdensity,
                   cmap=cmap, figsize=(5, 5),
                   verbose=True)
    plt.show()
