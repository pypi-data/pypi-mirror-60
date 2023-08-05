from functools import partial

import numpy as np
from sklearn.mixture import GaussianMixture

from spectral_connectivity import Connectivity, Multitaper

_DEFAULT_MULTITAPER_PARAMS = dict(time_halfbandwidth_product=1,
                                  time_window_duration=0.250,
                                  time_window_step=0.250)


def lfp_likelihood(spectral_rhythm_band_power, spectral_rhythm_model,
                   no_spectral_rhythm_model):
    """Estimates the likelihood of being in a spectral_rhythm state over time
    given the spectral power of the local field potentials (LFPs).

    Parameters
    ----------
    spectral_rhythm_band_power : ndarray, shape (n_time, n_signals)
    out_spectral_rhythm_kde : statsmodels.nonparametric.kernel_density.KDEMultivariate
    in_spectral_rhythm_kde : statsmodels.nonparametric.kernel_density.KDEMultivariate

    Returns
    -------
    log_likelihood : ndarray, shape (n_time, 2)

    """
    not_nan = np.all(~np.isnan(spectral_rhythm_band_power), axis=1)
    n_time = spectral_rhythm_band_power.shape[0]

    log_likelihood = np.ones((n_time, 2))

    log_likelihood[not_nan, 0] = no_spectral_rhythm_model.score_samples(
        np.log(spectral_rhythm_band_power[not_nan]))

    log_likelihood[not_nan, 1] = spectral_rhythm_model.score_samples(
        np.log(spectral_rhythm_band_power[not_nan]))

    return log_likelihood


def fit_lfp_likelihood(spectral_rhythm_band_power, is_spectral_rhythm,
                       model=GaussianMixture,
                       model_kwargs=dict(n_components=1)):
    """Fits the likelihood of being in a spectral_rhythm state over time given the
     spectral power of the local field potentials (LFPs).

    Parameters
    ----------
    spectral_rhythm_band_power : ndarray, shape (n_time, n_signals)
    is_spectral_rhythm : bool ndarray, shape (n_time,)
    sampling_frequency : float

    Returns
    -------
    likelihood_ratio : function

    """

    not_nan = np.all(~np.isnan(spectral_rhythm_band_power), axis=1)
    spectral_rhythm_model = model(**model_kwargs).fit(
        np.log(spectral_rhythm_band_power[is_spectral_rhythm & not_nan] +
               np.spacing(1)))
    no_spectral_rhythm_model = model(**model_kwargs).fit(
        np.log(spectral_rhythm_band_power[~is_spectral_rhythm & not_nan] +
               np.spacing(1)))

    return partial(lfp_likelihood, spectral_rhythm_model=spectral_rhythm_model,
                   no_spectral_rhythm_model=no_spectral_rhythm_model)


def estimate_spectral_rhythm_power(lfps, sampling_frequency,
                                   frequency_band=(10, 16), start_time=0.00,
                                   multitaper_params=_DEFAULT_MULTITAPER_PARAMS):
    """Estimates the spectral_rhythm power of each LFP.

    Parameters
    ----------
    lfps : ndarray, shape (n_time, n_signals)
    sampling_frequency : float
    frequency_band : (start_freq, end_freq)
    start_time : float
    multitaper_params : dict

    Returns
    -------
    time : ndarray, shape (n_time_windows,)
    spectral_rhythm_band_power : ndarray (n_time_windows, n_signals)

    """
    m = Multitaper(lfps, sampling_frequency=sampling_frequency,
                   **multitaper_params)
    c = Connectivity.from_multitaper(m)
    freq_ind = ((c.frequencies > frequency_band[0]) &
                (c.frequencies < frequency_band[1]))
    power = c.power()[..., freq_ind, :]

    return c.time, power
