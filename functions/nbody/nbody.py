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
                                  map_size: int, mesh_cells: int, *args) -> np.ndarray:

    # mean_value: mean value for the field
    # power_spectrum: P(k, *args) power spectrum for the field [(length units)^2]
    # map_size: side length for the map [length units]
    # mesh_cells: number of mesh cells for the field
    # periodic: should the map be considered to be periodic or not?
    # *args: extra arguments for power spectrum

    # TODO: Enforce Hermitian condition
    # TODO: Use real-to-real FFT
    # TODO: Generalise to nD

    # Parameters
    pad_fraction = 2  # Amount to increase size of array if non-periodic

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
    sigma_grid = np.sqrt(power_spectrum(k_grid, *args))/map_size
    x, y = np.random.normal(0., sigma_grid, size=(2, mesh_cells, mesh_cells))
    cfield = x + 1j*y

    # FFT
    cfield = np.fft.ifft2(cfield)
    cfield = cfield*mesh_cells**2  # Normalisation

    # Convert to real
    # For non-periodic arrays we discard some
    field = np.real(cfield[0:mesh_cells, 0:mesh_cells])
    return field


def make_image(params: dict, krange=(1e-3, 1e1), nk=128, z=0., L=512., n=512, log_normal=True, pad_inches=0.) -> bytes:

    # Ranges
    k = np.logspace(np.log10(krange[0]), np.log10(krange[-1]), nk)
    zs = [z]  # Redshifts

    # Constants
    As = 2.1e-9

    # Initial run of CAMB
    pars = camb.CAMBparams(WantCls=False)
    omega_c = params['Omega_m']*(params['H_0']/100.)**2
    omega_b = params['Omega_b']*(params['H_0']/100.)**2
    pars.set_cosmology(omch2=omega_c, ombh2=omega_b,
                       H0=params['H_0'], mnu=params['m_nu'])
    pars.set_dark_energy(
        w=params['w_0'], wa=params['w_a'], dark_energy_model='ppf')
    pars.InitPower.set_params(As=As, ns=params['n_s'])
    pars.set_matter_power(redshifts=zs, kmax=10.*krange[-1])

    # Scale 'As' to be correct for the desired 'sigma_8' value if necessary
    results = camb.get_results(pars)
    sigma_8_init = results.get_sigma8_0()
    scaling = (params['sigma_8']/sigma_8_init)**2
    As *= scaling
    pars.InitPower.set_params(As=As, ns=params['n_s'])

    # Run CAMB
    results = camb.get_results(pars)

    # HMcode
    Pk = hmcode.power(k, zs, results)[0]  # Isolate the z=0

    # Plot
    # for iz, z in enumerate(zs):
    #     plt.loglog(k, Pk[iz, :], label='z = {:1.1f}'.format(z))
    # plt.xlabel(r'$k$ $[h \mathrm{Mpc}^{-1}]$')
    # plt.ylabel(r'$P(k)$ $[(h^{-1}\mathrm{Mpc})^3]$')
    # plt.legend()
    # plt.show()

    def Pk_func(x, k, Pk, kmax):
        Pk = np.exp(np.interp(np.log(x), np.log(k),
                    np.log(Pk*np.exp(-k/kmax))))
        return Pk

    def Dk_func(x, k, Pk, kmax):
        Dk = 4.*np.pi*(x/(2.*np.pi))**3*Pk_func(x, k, Pk, kmax)
        return Dk

    # Calculate kmax_Pk from the power spectrum
    kmax_Pk = fsolve(lambda x: Dk_func(x, k, Pk, 100.)-1., 0.1)
    delta = make_Gaussian_random_field_2D(
        0., lambda x: Pk_func(x, k, Pk, kmax_Pk), L, n)
    # print(delta.min(), delta.max(), delta.mean(), delta.std())
    if log_normal:  # Log-normal transform
        delta = np.exp(delta)-1.
        delta = -1.+(1.+delta)/(1.+delta.mean())
        # print(delta.min(), delta.max(), delta.mean(), delta.std())

    eps = 1.+delta[delta > -1.].min()
    buffer = io.BytesIO()
    plt.subplots(figsize=(8, 8), dpi=224)
    plt.imshow(np.log(1.+delta+eps))
    plt.xticks([])
    plt.yticks([])
    plt.savefig(buffer, bbox_inches='tight',
                format='png', pad_inches=pad_inches)
    buffer = buffer.getvalue()
    return buffer   # Return the image binary (avoids saving to disk)


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

    np.random.seed(seed)

    _ = make_image(params, (kmin, kmax), nk, z, L, n)
    plt.show()
