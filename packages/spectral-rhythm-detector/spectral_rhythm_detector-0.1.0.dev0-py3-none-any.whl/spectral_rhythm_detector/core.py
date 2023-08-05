import numpy as np
import pandas as pd

from hmmlearn import hmm
from spectral_rhythm_detector.lfp_likelihood import (_DEFAULT_MULTITAPER_PARAMS,
                                                     estimate_spectral_rhythm_power)

_startprob_prior = np.log(np.array([np.spacing(1), 1.0 - np.spacing(1)]))
_DEFAULT_HMM_PARAMS = dict(n_components=2, covariance_type='full',
                           startprob_prior=_startprob_prior, n_iter=100,
                           tol=1E-6)


def atleast_2d(x):
    return np.atleast_2d(x).T if x.ndim < 2 else x


def detect_spectral_rhythm(time, lfps, sampling_frequency,
                           multitaper_params=_DEFAULT_MULTITAPER_PARAMS,
                           hmm_params=_DEFAULT_HMM_PARAMS,
                           frequency_band=(10, 16)):
    '''Find spectral rhythm times using spectral power and an HMM.

    Parameters
    ----------
    time : ndarray, shape (n_time,)
    lfps : ndarray, shape (n_time, n_signals)
    sampling_frequency : float
    multitaper_params : dict, optional
    hmm_params : dict, optional
    freq_band : tuple, optional

    Returns
    -------
    results : pandas.DataFrame, shape (n_time, 3)
    model : hmmlearn.GaussianHMM instance

    '''
    power_time, spectral_rhythm_band_power = estimate_spectral_rhythm_power(
        atleast_2d(lfps), sampling_frequency, start_time=time[0],
        multitaper_params=multitaper_params, frequency_band=frequency_band)
    spectral_rhythm_band_power = spectral_rhythm_band_power.reshape(
        (power_time.shape[0], -1))

    model = hmm.GaussianHMM(
        **hmm_params).fit(np.log(spectral_rhythm_band_power))

    state_ind = model.predict(np.log(spectral_rhythm_band_power))
    if (spectral_rhythm_band_power[state_ind == 0].mean() >
            spectral_rhythm_band_power[state_ind == 1].mean()):
        spectral_rhythm_ind = 0
    else:
        spectral_rhythm_ind = 1

    power_time = pd.Index(power_time, name='time')
    time = pd.Index(time, name='time')

    is_spectral_rhythm = np.zeros_like(state_ind, dtype=np.bool)
    is_spectral_rhythm[state_ind == spectral_rhythm_ind] = True
    is_spectral_rhythm = (pd.DataFrame(
        dict(is_spectral_rhythm=is_spectral_rhythm),
        index=power_time)
        .reindex(index=time, method='pad')
        .reset_index(drop=True))

    spectral_rhythm_probability = model.predict_proba(
        np.log(spectral_rhythm_band_power))
    spectral_rhythm_df = (pd.DataFrame(
        dict(probability=spectral_rhythm_probability[:, spectral_rhythm_ind]),
        index=power_time)
        .reindex(index=time)
        .reset_index(drop=True)
        .interpolate())

    spectral_rhythm_df = pd.concat(
        (spectral_rhythm_df, is_spectral_rhythm), axis=1).set_index(time)

    return spectral_rhythm_df, model
