from scipy.signal import welch
import numpy as np
import matplotlib.pyplot as plt

from .mfa import MFA


def plot_psd(signal, fs, n_fft=4096, segment_size=None, n_moments=2,
             log='log2'):
    """
    Plot the superposition of Fourier-based Welch estimation and Wavelet-based
    estimation of PSD on a log-log graphic.
    Based on the `wavelet_fourier_spectrum` function of the MATLAB toolbox
    mf_bs_toolbox-v0.2 found at
    http://www.ens-lyon.fr/PHYSIQUE/Equipe3/Multifractal/dat/mf_bs_tool-v0.2.zip

    Parameters
    ----------
    signal: 1D-array_like
        Time series of sampled values

    fs: float
        Sampling frequency of the signal

    n_fft: int, optional
        Length of the FFT desired.
        If `segment_size` is greater, ``n_fft = segment_size``.

    segment_size: int | None
        Length of Welch segments.
        Defaults to None, which sets it equal to `n_fft`

    n_moments: int
        Number of vanishing moments of the Daubechies wavelet used in the
        Wavelet decomposition.

    """

    # Computing

    freq_fourier, psd_fourier = welch_estimation(signal, fs, n_fft,
                                                 segment_size)
    freq_wavelet, psd_wavelet = wavelet_estimation(signal, fs, n_moments)

    # Plotting

    freq = [freq_fourier, freq_wavelet]
    psd = [psd_fourier, psd_wavelet]
    legend = ['Fourier', 'Wavelet']
    _log_plot(freq, psd, legend, log=log)


log_function = {'log2': np.log2,
                'log': np.log}


def _log_psd(freq, psd, log):

    # Avoid computing log(0)
    if np.any(freq == 0):
        support = [freq != 0.0][0]
        # from IPython.core.debugger import Pdb; Pdb().set_trace()
        freq, psd = freq[support], psd[support]

    # Compute the logged values of the frequency and psd
    log = log_function[log]
    freq, psd = log(freq), log(psd)

    return freq, psd


def _log_plot(freq_list, psd_list, legend=None, slope=None, log='log2'):

    for freq, psd in zip(freq_list, psd_list):
        freq, psd = _log_psd(freq, psd, log)  # Log frequency and psd
        plt.plot(freq, psd)

    if slope is not None:
        plt.plot(*slope, color='black')

    if legend is not None:
        plt.legend(legend)

    plt.xlabel('log_2 f')
    plt.ylabel('log_2 S(f)')
    plt.title('Power Spectral Density')

    plt.show()


def welch_estimation(signal, fs, n_fft=4096, segment_size=None):
    """
    Wrapper for scipy.signal.welch to compute the PSD using the Welch estimator

    Parameters
    ----------
    signal: 1D-array_like
        Time series of sampled values

    fs: float
        Sampling frequency of the signal

    n_fft: int, optional
        Length of the FFT desired.
        If `segment_size` is greater, ``n_fft = segment_size``.

    segment_size: int | None
        Length of Welch segments.
        Defaults to None, which sets it equal to `n_fft`
    """

    # Input argument sanitizing

    if segment_size is None:
        segment_size = n_fft

    if n_fft < segment_size:
        n_fft = segment_size

    # Frequency
    freq = fs * np.linspace(0, 0.5, n_fft / 2 + 1)

    # PSD
    _, psd = welch(signal,
                   window='hamming',
                   nperseg=segment_size,
                   noverlap=segment_size/2,
                   nfft=n_fft,
                   detrend=False,
                   return_onesided=True,
                   scaling='density',
                   average='mean',
                   fs=2 * np.pi)

    psd *= 4        # compensating for negative frequencies
    psd = np.array(psd)

    return freq, psd


def wavelet_estimation(signal, fs, n_moments=2):

    """
    PSD estimation using the Wavelet coefficients estimated through the
    `MFA` class

    Parameters
    ----------
    signal: 1D-array_like
        Time series of sampled values

    fs: float
        Sampling frequency of the signal

    n_moments: int
        Number of vanishing moments of the Daubechies wavelet used in the
        Wavelet decomposition.

    """

    # PSD
    mfa = MFA(wt_name=f'db{n_moments}',
              formalism='wcmf',
              j1=1,
              j2=13,
              n_cumul=2,
              gamint=1/2,
              wtype=0,
              p=np.inf)

    mfa._set_and_verify_parameters()

    mfa.wavelet_coeffs = None
    mfa.wavelet_leaders = None
    mfa.structure = None
    mfa.cumulants = None

    mfa._wavelet_analysis(signal)

    psd = [np.square(arr).mean() for arr in mfa.wavelet_coeffs.values.values()]
    psd = np.array(psd)

    # Frequency
    scale = np.arange(len(psd)) + 1
    freq = (3/4 * fs) / (np.power(2, scale))

    return freq, psd