# Standard imports
import io

# Third-party imports
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import camb
import hmcode
# from numba import njit, prange


# @njit(parallel=True)
def make_Gaussian_random_field_2D(mean_value: float, power_spectrum: np.ndarray,
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


def make_image(params: dict, krange=(1e-3, 1e1), nk=128, z=0., L=512., n=512,
               vrange=(None, None), box_h_units=True, truncate_Pk=True,
               log_normal_transform=True, plot_log_overdensity=True,
               norm_sigma8=True,
               pad_inches=0., cmap='CMRmap',
               verbose=False) -> bytes:

    # Constants
    kfac = 10.  # How much bigger is CAMB kmax

    # Ranges
    kmin, kmax = krange
    k = np.logspace(np.log10(kmin), np.log10(kmax), nk)
    zs = [z]  # Redshifts

    # Initial run of CAMB
    pars = camb.CAMBparams(WantCls=False)
    omega_c = params['Omega_m']*(params['H_0']/100.)**2
    omega_b = params['Omega_b']*(params['H_0']/100.)**2
    pars.set_cosmology(omch2=omega_c, ombh2=omega_b,
                       H0=params['H_0'], mnu=params['m_nu'])
    pars.set_dark_energy(
        w=params['w_0'], wa=params['w_a'], dark_energy_model='ppf')
    pars.InitPower.set_params(As=params['A_s'], ns=params['n_s'])
    pars.set_matter_power(redshifts=zs, kmax=kfac*kmax)

    # Scale 'As' to be correct for the desired 'sigma_8' value if necessary
    if norm_sigma8:
        results = camb.get_results(pars)
        sigma_8_init = results.get_sigma8_0()
        scaling = (params['sigma_8']/sigma_8_init)**2
        params['A_s'] *= scaling
        pars.InitPower.set_params(As=params['A_s'], ns=params['n_s'])

    # Run CAMB
    results = camb.get_results(pars)

    # HMcode
    Pk = hmcode.power(k, zs, results)[zs.index(z)]

    # Plot
    # for iz, z in enumerate(zs):
    #     plt.loglog(k, Pk[iz, :], label='z = {:1.1f}'.format(z))
    # plt.xlabel(r'$k$ $[h \mathrm{Mpc}^{-1}]$')
    # plt.ylabel(r'$P(k)$ $[(h^{-1}\mathrm{Mpc})^3]$')
    # plt.legend()
    # plt.show()

    def Pk_func(k, k_array, Pk_array):
        Pk = np.exp(np.interp(np.log(k), np.log(k_array), np.log(Pk_array)))
        return Pk

    def Dk_func(k, k_array, Pk_array):
        Dk = 4.*np.pi*(k/(2.*np.pi))**3*Pk_func(k, k_array, Pk_array)
        return Dk

    # TODO: Convert to 2D power spectrum

    # Calculate kmax_Pk from the power spectrum
    # Defined as a non-linear wavenumber where D^2(k_max)=1.
    if truncate_Pk:
        kmax_Pk = fsolve(lambda x: Dk_func(x, k, Pk)-1., 0.1)[0]
        if verbose:
            print(f"Truncation k: {kmax_Pk} h/Mpc")
        Pk *= np.exp(-k/kmax_Pk)

    # Generate Gaussian random field
    # TODO: Check the length transformation
    L_here = L if box_h_units else L/(params['H_0']/100.)
    delta = make_Gaussian_random_field_2D(
        0., lambda x: Pk_func(x, k, Pk), L_here, n)

    # Log-normal transform
    if log_normal_transform:
        delta = np.exp(delta)-1.
        delta = -1.+(1.+delta)/(1.+delta.mean())
    if verbose:
        print(f"Minimum and maximum field values: {delta.min(), delta.max()}")
        print(f"Mean and standard deviation: {delta.mean(), delta.std()}")
        print()

    # Plot
    plt.subplots(figsize=(8, 8), dpi=224)
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
        'n_s': 0.96,
        'm_nu': 0.,
    }
    kmin, kmax = 1e-3, 1e1
    nk = 100
    z = 0.
    L = 512.
    n = 512
    seed = 123
    vmin, vmax = 1e-3, 5000.
    cmap = 'cubehelix'

    np.random.seed(seed)

    _ = make_image(params, (kmin, kmax), nk, z, L, n,
                   vrange=(vmin, vmax), cmap=cmap, verbose=True)
    plt.show()
