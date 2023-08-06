"""
YASA (Yet Another Spindle Algorithm): fast and robust detection of spindles,
slow-waves, and rapid eye movements from sleep EEG recordings.

- Author: Raphael Vallat (www.raphaelvallat.com)
- GitHub: https://github.com/raphaelvallat/yasa
- License: BSD 3-Clause License
"""
import mne
import logging
import numpy as np
import pandas as pd
from scipy import signal
from mne.filter import filter_data
from scipy.interpolate import interp1d
from scipy.fftpack import next_fast_len

from .numba import _detrend, _rms
from .others import moving_transform, trimbothstd, _zerocrossings
from .spectral import stft_power

# Define YASA logger
logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

logger = logging.getLogger('yasa')

__all__ = ['spindles_detect', 'spindles_detect_multi', 'sw_detect',
           'sw_detect_multi', 'rem_detect', 'get_bool_vector',
           'get_sync_events']

#############################################################################
# HELPER FUNCTIONS
#############################################################################


def _merge_close(index, min_distance_ms, sf):
    """Merge events that are too close in time.

    Parameters
    ----------
    index : array_like
        Indices of supra-threshold events.
    min_distance_ms : int
        Minimum distance (ms) between two events to consider them as two
        distinct events
    sf : float
        Sampling frequency of the data (Hz)

    Returns
    -------
    f_index : array_like
        Filled (corrected) Indices of supra-threshold events

    Notes
    -----
    Original code imported from the Visbrain package.
    """
    # Convert min_distance_ms
    min_distance = min_distance_ms / 1000. * sf
    idx_diff = np.diff(index)
    condition = idx_diff > 1
    idx_distance = np.where(condition)[0]
    distance = idx_diff[condition]
    bad = idx_distance[np.where(distance < min_distance)[0]]
    # Fill gap between events separated with less than min_distance_ms
    if len(bad) > 0:
        fill = np.hstack([np.arange(index[j] + 1, index[j + 1])
                          for i, j in enumerate(bad)])
        f_index = np.sort(np.append(index, fill))
        return f_index
    else:
        return index


def _index_to_events(x):
    """Convert a 2D (start, end) array into a continuous one.

    Parameters
    ----------
    x : array_like
        2D array of indices.

    Returns
    -------
    index : array_like
        Continuous array of indices.

    Notes
    -----
    Original code imported from the Visbrain package.
    """
    index = np.array([])
    for k in range(x.shape[0]):
        index = np.append(index, np.arange(x[k, 0], x[k, 1] + 1))
    return index.astype(int)


def get_bool_vector(data=None, sf=None, detection=None):
    """Return a Boolean vector given the original data and sf and
    a YASA's detection dataframe.

    Parameters
    ----------
    data : array_like or :py:class:`mne.io.BaseRaw`
        1D or 2D EEG data. Can also be :py:class:`mne.io.BaseRaw`,
        in which case ``data`` and ``sf`` will be automatically extracted.
    sf : float
        The sampling frequency of ``data``.
        Can be omitted if ``data`` is a :py:class:`mne.io.BaseRaw`.
    detection : :py:class:`pandas.DataFrame`
        YASA's detection dataframe returned by the
        :py:func:`yasa.spindles_detect`, :py:func:`yasa.sw_detect`,
        or :py:func:`yasa.rem_detect` functions.

    Returns
    -------
    bool_vector : :py:class:`numpy.ndarray`
        Array of bool indicating for each sample in data if this sample is
        part of a detected event (True) or not (False).
    """
    # Check if input data is a MNE Raw object
    if isinstance(data, mne.io.BaseRaw):
        sf = data.info['sfreq']  # Extract sampling frequency
        data = data.get_data() * 1e6  # Convert from V to uV
        data = np.squeeze(data)  # Flatten if only one channel is present

    data = np.asarray(data)
    assert isinstance(detection, pd.DataFrame)
    assert 'Start' in detection.keys()
    assert 'End' in detection.keys()
    bool_vector = np.zeros(data.shape, dtype=int)

    # For multi-channel detection
    multi = False
    if 'Channel' in detection.keys():
        chan = detection['Channel'].unique()
        n_chan = chan.size
        multi = True if n_chan > 1 else False

    if multi:
        for c in chan:
            sp_chan = detection[detection['Channel'] == c]
            idx_sp = _index_to_events(sp_chan[['Start', 'End']].values * sf)
            bool_vector[sp_chan['IdxChannel'].iloc[0], idx_sp] = 1
    else:
        idx_sp = _index_to_events(detection[['Start', 'End']].values * sf)
        bool_vector[idx_sp] = 1
    return bool_vector


def get_sync_events(data=None, sf=None, detection=None, center='NegPeak',
                    time_before=0.4, time_after=0.8):
    """
    Return the raw data of each detected slow-waves / spindles, after
    centering to a specific timepoint.

    This function can be used to plot an average template of the
    detected slow-waves / spindles.

    Parameters
    ----------
    data : array_like or :py:class:`mne.io.BaseRaw`
        1D or 2D EEG data. Can also be :py:class:`mne.io.BaseRaw`,
        in which case ``data`` and ``sf`` will be automatically extracted.
    sf : float
        The sampling frequency of ``data``.
        Can be omitted if ``data`` is a :py:class:`mne.io.BaseRaw`.
    detection : :py:class:`pandas.DataFrame`
        YASA's detection dataframe returned by the
        :py:func:`yasa.sw_detect`, :py:func:`yasa.sp_detect`,
        :py:func:`yasa.sw_detect_multi`, or
        :py:func:`yasa.sp_detect_multi`, functions.
    center : str
        Landmark of the slow-waves / spindles to synchronize the timing on.
        Default is to use the negative peak.
    time_before : float
        Time (in seconds) before ``center``.
    time_after : float
        Time (in seconds) after ``center``.

    Returns
    -------
    df_sw : :py:class:`pandas.DataFrame`
        Ouput detection dataframe::

        'Event' : Event number
        'Time' : Timing of the events (in seconds)
        'Amplitude' : Raw data for event
        'Chan' : Channel (only in multi-channel detection)
    """
    # Check if input data is a MNE Raw object
    if isinstance(data, mne.io.BaseRaw):
        sf = data.info['sfreq']  # Extract sampling frequency
        data = data.get_data() * 1e6  # Convert from V to uV

    # Safety checks
    assert isinstance(data, np.ndarray), 'data must be a numpy array'
    assert isinstance(detection, pd.DataFrame), 'detection must be a dataframe'
    assert isinstance(sf, (int, float)), 'sf must be a float or an int'
    assert center in ['PosPeak', 'NegPeak', 'Peak', 'MidCrossing', 'Start',
                      'End'], 'center timepoint not recognized'

    if 'Channel' in detection.columns:
        # Multi-channel (recursive call)
        assert data.ndim > 1, 'Data must be 2D for multi-channel detection.'
        df_sync = pd.DataFrame()
        for c, k in detection.groupby('Channel'):
            idx_chan = k.iloc[0, -1]
            df_tmp = get_sync_events(data[idx_chan, :], sf, k.iloc[:, :-2],
                                     center=center, time_before=time_before,
                                     time_after=time_after)
            df_tmp['Channel'] = c
            df_tmp['IdxChannel'] = idx_chan
            df_sync = df_sync.append(df_tmp, ignore_index=True)
    else:
        # Single-channel
        data = np.squeeze(data)
        assert data.ndim == 1, 'Data must be 1D for single-channel detection.'
        # Define number of samples before and after the peak
        assert time_before >= 0
        assert time_after >= 0
        N_bef = int(sf * time_before)
        N_aft = int(sf * time_after)
        # Convert to integer sample indices in data
        idx_peak = (detection[center] * sf).astype(int).values[..., np.newaxis]

        def rng(x):
            """Utility function to create a range before and after
            a given value."""
            return np.arange(x - N_bef, x + N_aft + 1)

        # Extract indices, data, and time vector
        idx = np.apply_along_axis(rng, 1, idx_peak)
        # We drop the events for which the indices exceed data
        idx_mask = np.ma.mask_rows(np.ma.masked_outside(idx, 0, data.shape[0]))
        idx = np.ma.compress_rows(idx_mask)
        amps = data[idx]
        time = rng(0) / sf

        # Convert to dataframe
        df_sync = pd.DataFrame(amps.T)
        df_sync['Time'] = time
        df_sync = df_sync.melt(id_vars='Time', var_name='Event',
                               value_name='Amplitude')
    return df_sync


#############################################################################
# SPINDLES DETECTION
#############################################################################


def spindles_detect(data, sf, hypno=None, include=(1, 2, 3), freq_sp=(12, 15),
                    duration=(0.5, 2), freq_broad=(1, 30), min_distance=500,
                    downsample=True, thresh={'rel_pow': 0.2, 'corr': 0.65,
                    'rms': 1.5}, remove_outliers=False, coupling=False,
                    freq_so=(0.1, 1.25)):
    """Spindles detection.

    Parameters
    ----------
    data : array_like
        Single-channel continuous EEG data. Unit must be uV.

        .. warning::
            The default unit of :py:class:`mne.io.BaseRaw` is Volts.
            Therefore, if passing data from a :py:class:`mne.io.BaseRaw`,
            you need to multiply the data by 1e6 to convert to micro-Volts
            (1 V = 1,000,000 uV), e.g.:

            .. code-block:: python

                data = raw.get_data() * 1e6  # Make sure that data is in uV
    sf : float
        Sampling frequency of the data, in Hz.
    hypno : array_like
        Sleep stage vector (hypnogram). If the hypnogram is loaded, the
        detection will only be applied to the value defined in
        ``include`` (default = N1 + N2 + N3 sleep).

        The hypnogram must have the same number of samples as ``data``.
        To upsample your hypnogram, please refer to
        :py:func:`yasa.hypno_upsample_to_data`.

        .. note::
            The default hypnogram format in YASA is a 1D integer
            vector where:

            - -1 = Artefact / Movement
            - 0 = Wake
            - 1 = N1 sleep
            - 2 = N2 sleep
            - 3 = N3 sleep
            - 4 = REM sleep
    include : tuple, list or int
        Values in ``hypno`` that will be included in the mask. The default is
        (1, 2, 3), meaning that the detection is applied on N1, N2 and N3
        sleep. This has no effect when ``hypno`` is None.
    freq_sp : tuple or list
        Spindles frequency range. Default is 12 to 15 Hz. Please note that YASA
        uses a FIR filter (implemented in MNE) with a 1.5Hz transition band,
        which means that for `freq_sp = (12, 15 Hz)`, the -6 dB points are
        located at 11.25 and 15.75 Hz.
    duration : tuple or list
        The minimum and maximum duration of the spindles.
        Default is 0.5 to 2 seconds.
    freq_broad : tuple or list
        Broad band frequency of interest.
        Default is 1 to 30 Hz.
    min_distance : int
        If two spindles are closer than ``min_distance`` (in ms), they are
        merged into a single spindles. Default is 500 ms.
    downsample : boolean
        If True, the data will be downsampled to 100 Hz or 128 Hz (depending
        on whether the original sampling frequency is a multiple of 100 or 128,
        respectively).
    thresh : dict
        Detection thresholds::

            'rel_pow' : Relative power (= power ratio freq_sp / freq_broad).
            'corr' : Pearson correlation coefficient.
            'rms' : Mean(RMS) + 1.5 * STD(RMS).

        You can disable one or more threshold by putting ``None`` instead:

        .. code-block:: python

            thresh = {'rel_pow': None, 'corr': 0.65, 'rms': 1.5}
            thresh = {'rel_pow': None, 'corr': None, 'rms': 3}
    remove_outliers : boolean
        If True, YASA will automatically detect and remove outliers spindles
        using :py:class:`sklearn.ensemble.IsolationForest`.
        The outliers detection is performed on all the spindles
        parameters with the exception of the ``Start``, ``Peak``, ``End``,
        and ``SOPhase`` columns.
        YASA uses a random seed (42) to ensure reproducible results.
        Note that this step will only be applied if there are more than 50
        detected spindles in the first place. Default to False.
    coupling : boolean
        If True, YASA will also calculate the coupling between each detected
        spindles and the slow-oscillation signal. The coupling is given by the
        phase (in radians) of the filtered slow-oscillation signal
        at the most prominent peak of the spindles.

        Importantly, since the resulting variable is expressed in radians,
        one should use a circular mean to calculate the average across all
        events:

        .. code-block:: python

            from scipy.stats import circmean
            avg_SOPhase = circmean(sp['SOPhase'])

        For more details, please refer to the `Jupyter notebook
        <https://github.com/raphaelvallat/yasa/blob/master/notebooks/14_spindles-SO_coupling.ipynb>`_

        .. versionadded:: 0.1.9

    freq_so : tuple or list
        Slow-oscillations frequency of interest. This is only relevant if
        ``coupling=True``. Default is 0.1 to 1.25 Hz.

        .. versionadded:: 0.1.9

    Returns
    -------
    sp_params : :py:class:`pandas.DataFrame`
        Ouput detection dataframe::

            'Start' : Start time of each detected spindles (in seconds)
            'Peak': Timing of the most prominent spindles peak (in seconds)
            'End' : End time (in seconds)
            'Duration' : Duration (in seconds)
            'Amplitude' : Amplitude (in uV)
            'RMS' : Root-mean-square (in uV)
            'AbsPower' : Median absolute power (in log10 uV^2)
            'RelPower' : Median relative power (ranging from 0 to 1, in % uV^2)
            'Frequency' : Median frequency (in Hz)
            'Oscillations' : Number of oscillations (peaks)
            'Symmetry' : Symmetry index, ranging from 0 to 1
            'SOPhase': SO phase (radians) at the most prominent spindle peak
            'Stage' : Sleep stage (only if hypno was provided)

    Notes
    -----
    For better results, apply this detection only on artefact-free NREM sleep.

    For an example on how to run the detection, please refer to
    https://github.com/raphaelvallat/yasa/blob/master/notebooks/01_spindles_detection.ipynb
    """
    # Safety check
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 2:
        data = np.squeeze(data)
    assert data.ndim == 1, 'Wrong data dimension. Please pass 1D data.'
    freq_sp = sorted(freq_sp)
    freq_broad = sorted(freq_broad)
    assert isinstance(downsample, bool), 'Downsample must be True or False.'

    # Hypno processing
    if hypno is not None:
        hypno = np.asarray(hypno, dtype=int)
        assert hypno.ndim == 1, 'Hypno must be one dimensional.'
        assert hypno.size == data.size, 'Hypno must have same size as data.'
        unique_hypno = np.unique(hypno)
        logger.info('Number of unique values in hypno = %i', unique_hypno.size)
        # Check include
        assert include is not None, 'include cannot be None if hypno is given'
        include = np.atleast_1d(np.asarray(include))
        assert include.size >= 1, '`include` must have at least one element.'
        assert hypno.dtype.kind == include.dtype.kind, ('hypno and include '
                                                        'must have same dtype')
        if not np.in1d(hypno, include).any():
            logger.error('None of the stages specified in `include` '
                         'are present in hypno. Returning None.')
            return None

    # Check data amplitude
    data_trimstd = trimbothstd(data, cut=0.10)
    data_ptp = np.ptp(data)
    logger.info('Number of samples in data = %i', data.size)
    logger.info('Sampling frequency = %.2f Hz', sf)
    logger.info('Data duration = %.2f seconds', data.size / sf)
    logger.info('Trimmed standard deviation of data = %.4f uV', data_trimstd)
    logger.info('Peak-to-peak amplitude of data = %.4f uV', data_ptp)
    if not(1 < data_trimstd < 1e3 or 1 < data_ptp < 1e6):
        logger.error('Wrong data amplitude. Unit must be uV. Returning None.')
        return None

    # Check thresholds
    if 'rel_pow' not in thresh.keys():
        thresh['rel_pow'] = 0.20
    if 'corr' not in thresh.keys():
        thresh['corr'] = 0.65
    if 'rms' not in thresh.keys():
        thresh['rms'] = 1.5

    # Define which thresholds to use
    do_rel_pow = thresh['rel_pow'] not in [None, "none", "None"]
    do_corr = thresh['corr'] not in [None, "none", "None"]
    do_rms = thresh['rms'] not in [None, "none", "None"]
    n_thresh = sum([do_rel_pow, do_corr, do_rms])
    assert n_thresh >= 1, 'At least one threshold must be defined.'

    # Check if we can downsample to 100 or 128 Hz
    if downsample is True and sf > 128:
        if sf % 100 == 0 or sf % 128 == 0:
            new_sf = 100 if sf % 100 == 0 else 128
            fac = int(sf / new_sf)
            sf = new_sf
            data = data[::fac]
            logger.info('Downsampled data by a factor of %i', fac)
            if hypno is not None:
                hypno = hypno[::fac]
                assert hypno.size == data.size
        else:
            logger.warning("Cannot downsample if sf is not a mutiple of 100 "
                           "or 128. Skipping downsampling.")

    # Create sleep stage vector mask
    if hypno is not None:
        mask = np.in1d(hypno, include)
    else:
        mask = np.ones(data.size, dtype=bool)

    # Get data size and next fast length for Hilbert transform
    n = data.size
    nfast = next_fast_len(n)

    # Extract the SO signal for coupling
    if coupling:
        data_so = filter_data(data, sf, freq_so[0], freq_so[1], method='fir',
                              l_trans_bandwidth=0.1, h_trans_bandwidth=0.1,
                              verbose=0)
        # Now extract the instantaneous phase using Hilbert transform
        so_phase = np.angle(signal.hilbert(data_so, N=nfast)[:n])

    # Bandpass filter
    data = filter_data(data, sf, freq_broad[0], freq_broad[1], method='fir',
                       verbose=0)

    # The width of the transition band is set to 1.5 Hz on each side,
    # meaning that for freq_sp = (12, 15 Hz), the -6 dB points are located at
    # 11.25 and 15.75 Hz.
    data_sigma = filter_data(data, sf, freq_sp[0], freq_sp[1],
                             l_trans_bandwidth=1.5, h_trans_bandwidth=1.5,
                             method='fir', verbose=0)

    # Compute the pointwise relative power using interpolated STFT
    # Here we use a step of 200 ms to speed up the computation.
    # Note that even if the threshold is None we still need to calculate it for
    # the individual spindles parameter (RelPow).
    f, t, Sxx = stft_power(data, sf, window=2, step=.2, band=freq_broad,
                           interp=False, norm=True)
    idx_sigma = np.logical_and(f >= freq_sp[0], f <= freq_sp[1])
    rel_pow = Sxx[idx_sigma].sum(0)

    # Let's interpolate `rel_pow` to get one value per sample
    # Note that we could also have use the `interp=True` in the
    # `stft_power` function, however 2D interpolation is much slower than
    # 1D interpolation.
    func = interp1d(t, rel_pow, kind='cubic', bounds_error=False,
                    fill_value=0)
    t = np.arange(data.size) / sf
    rel_pow = func(t)

    # Now we apply moving RMS and correlation on the sigma-filtered signal
    if do_corr:
        _, mcorr = moving_transform(data_sigma, data, sf, window=.3, step=.1,
                                    method='corr', interp=True)
    if do_rms:
        _, mrms = moving_transform(data_sigma, data, sf, window=.3, step=.1,
                                   method='rms', interp=True)
        # Let's define the thresholds
        if hypno is None:
            thresh_rms = mrms.mean() + thresh['rms'] * \
                trimbothstd(mrms, cut=0.10)
        else:
            thresh_rms = mrms[mask].mean() + thresh['rms'] * \
                trimbothstd(mrms[mask], cut=0.10)
        # Avoid too high threshold caused by Artefacts / Motion during Wake.
        thresh_rms = min(thresh_rms, 10)
        logger.info('Moving RMS threshold = %.3f', thresh_rms)

    # Hilbert power (to define the instantaneous frequency / power)
    analytic = signal.hilbert(data_sigma, N=nfast)[:n]
    inst_phase = np.angle(analytic)
    inst_pow = np.square(np.abs(analytic))
    inst_freq = (sf / (2 * np.pi) * np.ediff1d(inst_phase))

    # Boolean vector of supra-threshold indices
    idx_sum = np.zeros(n)
    if do_rel_pow:
        idx_rel_pow = (rel_pow >= thresh['rel_pow']).astype(int)
        idx_sum += idx_rel_pow
        logger.info('N supra-theshold relative power = %i', idx_rel_pow.sum())
    if do_corr:
        idx_mcorr = (mcorr >= thresh['corr']).astype(int)
        idx_sum += idx_mcorr
        logger.info('N supra-theshold moving corr = %i', idx_mcorr.sum())
    if do_rms:
        idx_mrms = (mrms >= thresh_rms).astype(int)
        idx_sum += idx_mrms
        logger.info('N supra-theshold moving RMS = %i', idx_mrms.sum())

    # Make sure that we do not detect spindles in REM or Wake if hypno != None
    if hypno is not None:
        idx_sum[~mask] = 0

    # The detection using the three thresholds tends to underestimate the
    # real duration of the spindle. To overcome this, we compute a soft
    # threshold by smoothing the idx_sum vector with a 100 ms window.
    w = int(0.1 * sf)
    idx_sum = np.convolve(idx_sum, np.ones(w) / w, mode='same')
    # And we then find indices that are strictly greater than 2, i.e. we find
    # the 'true' beginning and 'true' end of the events by finding where at
    # least two out of the three treshold were crossed.
    where_sp = np.where(idx_sum > (n_thresh - 1))[0]

    # If no events are found, return an empty dataframe
    if not len(where_sp):
        logger.warning('No spindles were found in data. Returning None.')
        return None

    # Merge events that are too close
    if min_distance is not None and min_distance > 0:
        where_sp = _merge_close(where_sp, min_distance, sf)

    # Extract start, end, and duration of each spindle
    sp = np.split(where_sp, np.where(np.diff(where_sp) != 1)[0] + 1)
    idx_start_end = np.array([[k[0], k[-1]] for k in sp]) / sf
    sp_start, sp_end = idx_start_end.T
    sp_dur = sp_end - sp_start

    # Find events with bad duration
    good_dur = np.logical_and(sp_dur > duration[0], sp_dur < duration[1])

    # If no events of good duration are found, return an empty dataframe
    if all(~good_dur):
        logger.warning('No spindles were found in data. Returning None.')
        return None

    # Initialize empty variables
    n_sp = len(sp)
    sp_amp = np.zeros(n_sp)
    sp_freq = np.zeros(n_sp)
    sp_rms = np.zeros(n_sp)
    sp_osc = np.zeros(n_sp)
    sp_sym = np.zeros(n_sp)
    sp_abs = np.zeros(n_sp)
    sp_rel = np.zeros(n_sp)
    sp_sta = np.zeros(n_sp)
    sp_pro = np.zeros(n_sp)
    sp_cou = np.zeros(n_sp)

    # Number of oscillations (= number of peaks separated by at least 60 ms)
    # --> 60 ms because 1000 ms / 16 Hz = 62.5 ms, in other words, at 16 Hz,
    # peaks are separated by 62.5 ms. At 11 Hz, peaks are separated by 90 ms.
    distance = 60 * sf / 1000

    for i in np.arange(len(sp))[good_dur]:
        # Important: detrend the signal to avoid wrong peak-to-peak amplitude
        sp_x = np.arange(data[sp[i]].size, dtype=np.float64)
        sp_det = _detrend(sp_x, data[sp[i]])
        # sp_det = signal.detrend(data[sp[i]], type='linear')
        sp_amp[i] = np.ptp(sp_det)  # Peak-to-peak amplitude
        sp_rms[i] = _rms(sp_det)  # Root mean square
        sp_rel[i] = np.median(rel_pow[sp[i]])  # Median relative power

        # Hilbert-based instantaneous properties
        sp_inst_freq = inst_freq[sp[i]]
        sp_inst_pow = inst_pow[sp[i]]
        sp_abs[i] = np.median(np.log10(sp_inst_pow[sp_inst_pow > 0]))
        sp_freq[i] = np.median(sp_inst_freq[sp_inst_freq > 0])

        # Number of oscillations
        peaks, peaks_params = signal.find_peaks(sp_det,
                                                distance=distance,
                                                prominence=(None, None))
        sp_osc[i] = len(peaks)

        # For frequency and amplitude, we can also optionally use these
        # faster alternatives. If we use them, we do not need to compute the
        # Hilbert transform of the filtered signal.
        # sp_freq[i] = sf / np.mean(np.diff(peaks))
        # sp_amp[i] = peaks_params['prominences'].max()

        # Peak location & symmetry index
        # pk is expressed in sample since the beginning of the spindle
        pk = peaks[peaks_params['prominences'].argmax()]
        sp_pro[i] = sp_start[i] + pk / sf
        sp_sym[i] = pk / sp_det.size

        # SO-spindles coupling
        if coupling:
            sp_cou[i] = so_phase[sp[i]][pk]

        # Sleep stage
        if hypno is not None:
            sp_sta[i] = hypno[sp[i]][0]

    # Create a dictionnary
    sp_params = {'Start': sp_start,
                 'Peak': sp_pro,
                 'End': sp_end,
                 'Duration': sp_dur,
                 'Amplitude': sp_amp,
                 'RMS': sp_rms,
                 'AbsPower': sp_abs,
                 'RelPower': sp_rel,
                 'Frequency': sp_freq,
                 'Oscillations': sp_osc,
                 'Symmetry': sp_sym,
                 'SOPhase': sp_cou,
                 'Stage': sp_sta}

    df_sp = pd.DataFrame.from_dict(sp_params)[good_dur].reset_index(drop=True)

    if hypno is None:
        df_sp = df_sp.drop(columns=['Stage'])
    else:
        df_sp['Stage'] = df_sp['Stage'].astype(int).astype('category')

    if not coupling:
        df_sp = df_sp.drop(columns=['SOPhase'])

    # We need at least 50 detected spindles to apply the Isolation Forest.
    if remove_outliers and df_sp.shape[0] >= 50:
        from sklearn.ensemble import IsolationForest
        df_sp_dummies = pd.get_dummies(df_sp)
        col_keep = df_sp_dummies.columns.difference(['Start', 'Peak', 'End',
                                                     'SOPhase'])
        ilf = IsolationForest(behaviour='new', contamination='auto',
                              max_samples='auto', verbose=0, random_state=42)

        good = ilf.fit_predict(df_sp_dummies[col_keep])
        good[good == -1] = 0
        logger.info('%i outliers were removed.', (good == 0).sum())
        # Remove outliers from DataFrame
        df_sp = df_sp[good.astype(bool)].reset_index(drop=True)

    logger.info('%i spindles were found in data.', df_sp.shape[0])
    return df_sp


def spindles_detect_multi(data, sf=None, ch_names=None, multi_only=False,
                          **kwargs):
    """Multi-channel spindles detection.

    Parameters
    ----------
    data : array_like
        Multi-channel data. Unit must be uV and shape (n_chan, n_samples).
        Can also be a :py:class:`mne.io.BaseRaw`, in which case ``data``,
        ``sf``, and ``ch_names`` will be automatically extracted,
        and ``data`` will also be automatically converted from Volts (MNE)
        to micro-Volts (YASA).
    sf : float
        Sampling frequency of the data in Hz.
        Can be omitted if ``data`` is a :py:class:`mne.io.BaseRaw`.
    ch_names : list of str
        Channel names. Can be omitted if ``data`` is a
        :py:class:`mne.io.BaseRaw`.
    multi_only : boolean
        Define the behavior of the multi-channel detection. If True, only
        spindles that are present on at least two channels are kept. If False,
        no selection is applied and the output is just a concatenation of the
        single-channel detection dataframe. Default is False.
    **kwargs
        Keywords arguments that are passed to the
        :py:func:`yasa.spindles_detect` function.

    Returns
    -------
    sp_params : :py:class:`pandas.DataFrame`
        Ouput detection dataframe::

            'Start' : Start time of each detected spindles (in seconds)
            'Peak': Timing of the most prominent spindles peak (in seconds)
            'End' : End time (in seconds)
            'Duration' : Duration (in seconds)
            'Amplitude' : Amplitude (in uV)
            'RMS' : Root-mean-square (in uV)
            'AbsPower' : Median absolute power (in log10 uV^2)
            'RelPower' : Median relative power (ranging from 0 to 1, in % uV^2)
            'Frequency' : Median frequency (in Hz)
            'Oscillations' : Number of oscillations (peaks)
            'Symmetry' : Symmetry index, ranging from 0 to 1
            'Channel' : Channel name
            'IdxChannel' : Integer index of channel in data
            'Stage' : Sleep stage (only if hypno was provided)

    Notes
    -----
    For an example of how to run the detection, please refer to
    https://github.com/raphaelvallat/yasa/blob/master/notebooks/02_spindles_detection_multi.ipynb
    """
    # Check if input data is a MNE Raw object
    if isinstance(data, mne.io.BaseRaw):
        sf = data.info['sfreq']  # Extract sampling frequency
        ch_names = data.ch_names  # Extract channel names
        data = data.get_data() * 1e6  # Convert from V to uV
    else:
        assert sf is not None, 'sf must be specified if not using MNE Raw.'
        assert ch_names is not None, ('ch_names must be specified if not '
                                      'using MNE Raw.')

    # Safety check
    data = np.asarray(data, dtype=np.float64)
    assert data.ndim == 2
    assert data.shape[0] < data.shape[1]
    n_chan = data.shape[0]
    assert isinstance(ch_names, (list, np.ndarray))
    if len(ch_names) != n_chan:
        raise AssertionError('ch_names must have same length as data.shape[0]')

    # Single channel detection
    df = pd.DataFrame()
    for i in range(n_chan):
        df_chan = spindles_detect(data[i, :], sf, **kwargs)
        if df_chan is not None:
            df_chan['Channel'] = ch_names[i]
            df_chan['IdxChannel'] = i
            df = df.append(df_chan, ignore_index=True)
        else:
            logger.warning('No spindles were found in channel %s.',
                           ch_names[i])

    # If no spindles were detected, return None
    if df.empty:
        logger.warning('No spindles were found in data. Returning None.')
        return None

    # Find spindles that are present on at least two channels
    if multi_only and df['Channel'].unique().size > 1:
        # We round to the nearest second
        idx_good = np.logical_or(df['Start'].round(0).duplicated(keep=False),
                                 df['End'].round(0).duplicated(keep=False)
                                 ).to_list()
        return df[idx_good].reset_index(drop=True)
    else:
        return df


#############################################################################
# SLOW-WAVES DETECTION
#############################################################################


def sw_detect(data, sf, hypno=None, include=(2, 3), freq_sw=(0.3, 3.5),
              dur_neg=(0.3, 1.5), dur_pos=(0.1, 1), amp_neg=(40, 300),
              amp_pos=(10, 200), amp_ptp=(75, 500), downsample=True,
              remove_outliers=False):
    """Slow-waves detection.

    Parameters
    ----------
    data : array_like
        Single-channel continuous EEG data. Unit must be uV.

        .. warning::
            The default unit of :py:class:`mne.io.BaseRaw` is Volts.
            Therefore, if passing data from a :py:class:`mne.io.BaseRaw`,
            you need to multiply the data by 1e6 to convert to micro-Volts
            (1 V = 1,000,000 uV), e.g.:

            .. code-block:: ruby

                data = raw.get_data() * 1e6  # Make sure that data is in uV
    sf : float
        Sampling frequency of the data, in Hz.
    hypno : array_like
        Sleep stage vector (hypnogram). If the hypnogram is loaded, the
        detection will only be applied to the value defined in
        ``include`` (default = N2 + N3 sleep).

        The hypnogram must have the same number of samples as ``data``.
        To upsample your hypnogram, please refer to
        :py:func:`yasa.hypno_upsample_to_data`.

        .. note::
            The default hypnogram format in YASA is a 1D integer
            vector where:

            - -1 = Artefact / Movement
            - 0 = Wake
            - 1 = N1 sleep
            - 2 = N2 sleep
            - 3 = N3 sleep
            - 4 = REM sleep
    include : tuple, list or int
        Values in ``hypno`` that will be included in the mask. The default is
        (2, 3), meaning that the detection is applied on N2 and N3
        sleep. This has no effect when ``hypno`` is None.
    freq_sw : tuple or list
        Slow wave frequency range. Default is 0.3 to 3.5 Hz. Please note that
        YASA uses a FIR filter (implemented in MNE) with a 0.2Hz transition
        band, which means that for `freq_sw = (.3, 3.5 Hz)`, the -6 dB points
        are located at 0.2 and 3.6 Hz.
    dur_neg : tuple or list
        The minimum and maximum duration of the negative deflection of the
        slow wave. Default is 0.3 to 1.5 second.
    dur_pos : tuple or list
        The minimum and maximum duration of the positive deflection of the
        slow wave. Default is 0.1 to 1 second.
    amp_neg : tuple or list
        Absolute minimum and maximum negative trough amplitude of the
        slow-wave. Default is 40 uV to 300 uV.
    amp_pos : tuple or list
        Absolute minimum and maximum positive peak amplitude of the
        slow-wave. Default is 10 uV to 200 uV.
    amp_ptp : tuple or list
        Minimum and maximum peak-to-peak amplitude of the slow-wave.
        Default is 75 uV to 500 uV.
    downsample : boolean
        If True, the data will be downsampled to 100 Hz or 128 Hz (depending
        on whether the original sampling frequency is a multiple of 100 or 128,
        respectively).
    remove_outliers : boolean
        If True, YASA will automatically detect and remove outliers slow-waves
        using :py:class:`sklearn.ensemble.IsolationForest`.
        The outliers detection is performed on the frequency, amplitude and
        duration parameters of the detected slow-waves. YASA uses a random seed
        (42) to ensure reproducible results. Note that this step will only be
        applied if there are more than 100 detected slow-waves in the first
        place. Default to False.

    Returns
    -------
    sw_params : :py:class:`pandas.DataFrame`
        Ouput detection dataframe::

            'Start' : Start of each detected slow-wave (in seconds of data)
            'NegPeak' : Location of the negative peak (in seconds of data)
            'MidCrossing' : Location of the negative-to-positive zero-crossing
            'Pospeak' : Location of the positive peak
            'End' : End time (in seconds)
            'Duration' : Duration (in seconds)
            'ValNegPeak' : Amplitude of the negative peak (in uV - filtered)
            'ValPosPeak' : Amplitude of the positive peak (in uV - filtered)
            'PTP' : Peak to peak amplitude (ValPosPeak - ValNegPeak)
            'Slope' : Slope between ``NegPeak`` and ``MidCrossing`` (in uV/sec)
            'Frequency' : Frequency of the slow-wave (1 / ``Duration``)
            'Stage' : Sleep stage (only if hypno was provided)

    Notes
    -----
    For better results, apply this detection only on artefact-free NREM sleep.

    Note that the ``PTP``, ``Slope``, ``ValNegPeak`` and ``ValPosPeak`` are
    all computed on the filtered signal.

    For an example of how to run the detection, please refer to
    https://github.com/raphaelvallat/yasa/blob/master/notebooks/06_sw_detection.ipynb
    """
    # Safety check
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 2:
        data = np.squeeze(data)
    assert data.ndim == 1, 'Wrong data dimension. Please pass 1D data.'
    freq_sw = sorted(freq_sw)
    amp_ptp = sorted(amp_ptp)
    assert isinstance(downsample, bool), 'Downsample must be True or False.'

    # Hypno processing
    if hypno is not None:
        hypno = np.asarray(hypno, dtype=int)
        assert hypno.ndim == 1, 'Hypno must be one dimensional.'
        assert hypno.size == data.size, 'Hypno must have same size as data.'
        unique_hypno = np.unique(hypno)
        logger.info('Number of unique values in hypno = %i', unique_hypno.size)
        # Check include
        assert include is not None, 'include cannot be None if hypno is given'
        include = np.atleast_1d(np.asarray(include))
        assert include.size >= 1, '`include` must have at least one element.'
        assert hypno.dtype.kind == include.dtype.kind, ('hypno and include '
                                                        'must have same dtype')
        if not np.in1d(hypno, include).any():
            logger.error('None of the stages specified in `include` '
                         'are present in hypno. Returning None.')
            return None

    # Check data amplitude
    data_trimstd = trimbothstd(data, cut=0.10)
    data_ptp = np.ptp(data)
    logger.info('Number of samples in data = %i', data.size)
    logger.info('Sampling frequency = %.2f Hz', sf)
    logger.info('Data duration = %.2f seconds', data.size / sf)
    logger.info('Trimmed standard deviation of data = %.4f uV', data_trimstd)
    logger.info('Peak-to-peak amplitude of data = %.4f uV', data_ptp)
    if not(1 < data_trimstd < 1e3 or 1 < data_ptp < 1e6):
        logger.error('Wrong data amplitude. Unit must be uV. Returning None.')
        return None

    # Check if we can downsample to 100 or 128 Hz
    if downsample is True and sf > 128:
        if sf % 100 == 0 or sf % 128 == 0:
            new_sf = 100 if sf % 100 == 0 else 128
            fac = int(sf / new_sf)
            sf = new_sf
            data = data[::fac]
            logger.info('Downsampled data by a factor of %i', fac)
            if hypno is not None:
                hypno = hypno[::fac]
                assert hypno.size == data.size
        else:
            logger.warning("Cannot downsample if sf is not a mutiple of 100 "
                           "or 128. Skipping downsampling.")

    # Define time vector
    times = np.arange(data.size) / sf

    # Bandpass filter
    data_filt = filter_data(data, sf, freq_sw[0], freq_sw[1], method='fir',
                            verbose=0, l_trans_bandwidth=0.2,
                            h_trans_bandwidth=0.2)

    # Find peaks in data
    # Negative peaks with value comprised between -40 to -300 uV
    idx_neg_peaks, _ = signal.find_peaks(-1 * data_filt, height=amp_neg)

    # Positive peaks with values comprised between 10 to 150 uV
    idx_pos_peaks, _ = signal.find_peaks(data_filt, height=amp_pos)

    # Intersect with sleep stage vector
    if hypno is not None:
        mask = np.in1d(hypno, include)
        idx_mask = np.where(mask)[0]
        idx_neg_peaks = np.intersect1d(idx_neg_peaks, idx_mask,
                                       assume_unique=True)
        idx_pos_peaks = np.intersect1d(idx_pos_peaks, idx_mask,
                                       assume_unique=True)

    # If no peaks are detected, return None
    if len(idx_neg_peaks) == 0 or len(idx_pos_peaks) == 0:
        logger.warning('No peaks were found in data. Returning None.')
        return None

    # Make sure that the last detected peak is a positive one
    if idx_pos_peaks[-1] < idx_neg_peaks[-1]:
        # If not, append a fake positive peak one sample after the last neg
        idx_pos_peaks = np.append(idx_pos_peaks, idx_neg_peaks[-1] + 1)

    # For each negative peak, we find the closest following positive peak
    pk_sorted = np.searchsorted(idx_pos_peaks, idx_neg_peaks)
    closest_pos_peaks = idx_pos_peaks[pk_sorted] - idx_neg_peaks
    closest_pos_peaks = closest_pos_peaks[np.nonzero(closest_pos_peaks)]
    idx_pos_peaks = idx_neg_peaks + closest_pos_peaks

    # Now we compute the PTP amplitude and keep only the good peaks
    sw_ptp = np.abs(data_filt[idx_neg_peaks]) + data_filt[idx_pos_peaks]
    good_ptp = np.logical_and(sw_ptp > amp_ptp[0], sw_ptp < amp_ptp[1])

    # If good_ptp is all False
    if all(~good_ptp):
        logger.warning('No slow-wave with good amplitude. Returning None.')
        return None

    sw_ptp = sw_ptp[good_ptp]
    idx_neg_peaks = idx_neg_peaks[good_ptp]
    idx_pos_peaks = idx_pos_peaks[good_ptp]

    # Now we need to check the negative and positive phase duration
    # For that we need to compute the zero crossings of the filtered signal
    zero_crossings = _zerocrossings(data_filt)
    # Make sure that there is a zero-crossing after the last detected peak
    if zero_crossings[-1] < max(idx_pos_peaks[-1], idx_neg_peaks[-1]):
        # If not, append the index of the last peak
        zero_crossings = np.append(zero_crossings,
                                   max(idx_pos_peaks[-1], idx_neg_peaks[-1]))

    # Find distance to previous and following zc
    neg_sorted = np.searchsorted(zero_crossings, idx_neg_peaks)
    previous_neg_zc = zero_crossings[neg_sorted - 1] - idx_neg_peaks
    following_neg_zc = zero_crossings[neg_sorted] - idx_neg_peaks
    neg_phase_dur = (np.abs(previous_neg_zc) + following_neg_zc) / sf

    # Distance (in samples) between the positive peaks and the previous and
    # following zero-crossings
    pos_sorted = np.searchsorted(zero_crossings, idx_pos_peaks)
    previous_pos_zc = zero_crossings[pos_sorted - 1] - idx_pos_peaks
    following_pos_zc = zero_crossings[pos_sorted] - idx_pos_peaks
    pos_phase_dur = (np.abs(previous_pos_zc) + following_pos_zc) / sf

    # We now compute a set of metrics
    sw_start = times[idx_neg_peaks + previous_neg_zc]  # Start in time vector
    sw_end = times[idx_pos_peaks + following_pos_zc]  # End in time vector
    sw_dur = sw_end - sw_start  # Same as pos_phase_dur + neg_phase_dur
    sw_midcrossing = times[idx_neg_peaks + following_neg_zc]  # Neg-to-pos zc
    sw_idx_neg = times[idx_neg_peaks]  # Location of negative peak
    sw_idx_pos = times[idx_pos_peaks]  # Location of positive peak
    # Slope between peak trough and midcrossing
    sw_slope = sw_ptp / (sw_midcrossing - sw_idx_neg)
    # Hypnogram
    if hypno is not None:
        sw_sta = hypno[idx_neg_peaks]
    else:
        sw_sta = np.zeros(sw_dur.shape)

    # And we apply a set of thresholds to remove bad slow waves
    good_sw = np.logical_and.reduce((
                                    # Data edges
                                    previous_neg_zc != 0,
                                    following_neg_zc != 0,
                                    previous_pos_zc != 0,
                                    following_pos_zc != 0,
                                    # Duration criteria
                                    neg_phase_dur > dur_neg[0],
                                    neg_phase_dur < dur_neg[1],
                                    pos_phase_dur > dur_pos[0],
                                    pos_phase_dur < dur_pos[1],
                                    # Sanity checks
                                    sw_midcrossing > sw_start,
                                    sw_midcrossing < sw_end,
                                    sw_slope > 0,
                                    ))

    if all(~good_sw):
        logger.warning('No slow-wave satisfying all criteria. Returning None.')
        return None

    # Create a dictionnary and then a dataframe (much faster)
    sw_params = {'Start': sw_start,
                 'NegPeak': sw_idx_neg,
                 'MidCrossing': sw_midcrossing,
                 'PosPeak': sw_idx_pos,
                 'End': sw_end,
                 'Duration': sw_dur,
                 'ValNegPeak': data_filt[idx_neg_peaks],
                 'ValPosPeak': data_filt[idx_pos_peaks],
                 'PTP': sw_ptp,
                 'Slope': sw_slope,
                 'Frequency': 1 / sw_dur,
                 'Stage': sw_sta,
                 }

    df_sw = pd.DataFrame.from_dict(sw_params)[good_sw]

    # Remove all duplicates
    df_sw = df_sw.drop_duplicates(subset=['Start'], keep=False)
    df_sw = df_sw.drop_duplicates(subset=['End'], keep=False)

    if hypno is None:
        df_sw = df_sw.drop(columns=['Stage'])
    else:
        df_sw['Stage'] = df_sw['Stage'].astype(int).astype('category')

    # We need at least 100 detected slow waves to apply the Isolation Forest.
    if remove_outliers and df_sw.shape[0] >= 100:
        from sklearn.ensemble import IsolationForest
        col_keep = ['Duration', 'ValNegPeak', 'ValPosPeak', 'PTP', 'Slope',
                    'Frequency']
        ilf = IsolationForest(behaviour='new', contamination='auto',
                              max_samples='auto', verbose=0, random_state=42)

        good = ilf.fit_predict(df_sw[col_keep])
        good[good == -1] = 0
        logger.info('%i outliers were removed.', (good == 0).sum())
        # Remove outliers from DataFrame
        df_sw = df_sw[good.astype(bool)]

    logger.info('%i slow-waves were found in data.', df_sw.shape[0])
    return df_sw.reset_index(drop=True)


def sw_detect_multi(data, sf=None, ch_names=None, **kwargs):
    """Multi-channel slow-waves detection.

    Parameters
    ----------
    data : array_like
        Multi-channel data. Unit must be uV and shape (n_chan, n_samples).
        Can also be a :py:class:`mne.io.BaseRaw`, in which case ``data``,
        ``sf``, and ``ch_names`` will be automatically extracted,
        and ``data`` will also be automatically converted from Volts (MNE)
        to micro-Volts (YASA).
    sf : float
        Sampling frequency of the data in Hz.
        Can be omitted if ``data`` is a :py:class:`mne.io.BaseRaw`.
    ch_names : list of str
        Channel names. Can be omitted if ``data`` is a
        :py:class:`mne.io.BaseRaw`.
    **kwargs
        Keywords arguments that are passed to the :py:func:`yasa.sw_detect`
        function.

    Returns
    -------
    sw_params : :py:class:`pandas.DataFrame`
        Ouput detection dataframe::

            'Start' : Start of each detected slow-wave (in seconds of data)
            'NegPeak' : Location of the negative peak (in seconds of data)
            'MidCrossing' : Location of the negative-to-positive zero-crossing
            'Pospeak' : Location of the positive peak
            'End' : End time (in seconds)
            'Duration' : Duration (in seconds)
            'ValNegPeak' : Amplitude of the negative peak (in uV - filtered)
            'ValPosPeak' : Amplitude of the positive peak (in uV - filtered)
            'PTP' : Peak to peak amplitude (ValPosPeak - ValNegPeak)
            'Slope' : Slope between ``NegPeak`` and ``MidCrossing`` (in uV/sec)
            'Frequency' : Frequency of the slow-wave (1 / ``Duration``)
            'Stage' : Sleep stage (only if hypno was provided)
            'Channel' : Channel name
            'IdxChannel' : Integer index of channel in data

    Notes
    -----
    For better results, apply this detection only on artefact-free NREM sleep.

    Note that the ``PTP``, ``Slope``, ``ValNegPeak`` and ``ValPosPeak`` are
    computed on the filtered signal.

    For an example of how to run the detection, please refer to
    https://github.com/raphaelvallat/yasa/blob/master/notebooks/07_sw_detection_multi.ipynb
    """
    # Check if input data is a MNE Raw object
    if isinstance(data, mne.io.BaseRaw):
        sf = data.info['sfreq']  # Extract sampling frequency
        ch_names = data.ch_names  # Extract channel names
        data = data.get_data() * 1e6  # Convert from V to uV
    else:
        assert sf is not None, 'sf must be specified if not using MNE Raw.'
        assert ch_names is not None, ('ch_names must be specified if not '
                                      'using MNE Raw.')

    # Safety check
    data = np.asarray(data, dtype=np.float64)
    assert data.ndim == 2
    assert data.shape[0] < data.shape[1]
    n_chan = data.shape[0]
    assert isinstance(ch_names, (list, np.ndarray))
    if len(ch_names) != n_chan:
        raise AssertionError('ch_names must have same length as data.shape[0]')

    # Single channel detection
    df = pd.DataFrame()
    for i in range(n_chan):
        df_chan = sw_detect(data[i, :], sf, **kwargs)
        if df_chan is not None:
            df_chan['Channel'] = ch_names[i]
            df_chan['IdxChannel'] = i
            df = df.append(df_chan, ignore_index=True)
        else:
            logger.warning('No slow-waves were found in channel %s.',
                           ch_names[i])

    # If no slow-waves were detected, return None
    if df.empty:
        logger.warning('No slow-waves were found in data. Returning None.')
        return None

    return df


#############################################################################
# REMs DETECTION
#############################################################################


def rem_detect(loc, roc, sf, hypno=None, include=4, amplitude=(50, 325),
               duration=(0.3, 1.2), freq_rem=(0.5, 5), downsample=True,
               remove_outliers=False):
    """Rapid Eye Movements (REMs) detection.

    This detection requires both the left EOG (LOC) and right EOG (LOC).
    The units of the data must be uV. The algorithm is based on an amplitude
    thresholding of the negative product of the LOC and ROC
    filtered signal.

    .. versionadded:: 0.1.5

    Parameters
    ----------
    loc, roc : array_like
        Continuous EOG data (Left and Right Ocular Canthi, LOC / ROC) channels.
        Unit must be uV.

        .. warning::
            The default unit of :py:class:`mne.io.BaseRaw` is Volts.
            Therefore, if passing data from a :py:class:`mne.io.BaseRaw`,
            you need to multiply the data by 1e6 to convert to micro-Volts
            (1 V = 1,000,000 uV), e.g.:

            .. code-block:: ruby

                data = raw.get_data() * 1e6  # Make sure that data is in uV
    sf : float
        Sampling frequency of the data, in Hz.
    hypno : array_like
        Sleep stage vector (hypnogram). If the hypnogram is loaded, the
        detection will only be applied to the value defined in
        ``include`` (default = REM sleep).

        The hypnogram must have the same number of samples as ``data``.
        To upsample your hypnogram, please refer to
        :py:func:`yasa.hypno_upsample_to_data`.

        .. note::
            The default hypnogram format in YASA is a 1D integer
            vector where:

            - -1 = Artefact / Movement
            - 0 = Wake
            - 1 = N1 sleep
            - 2 = N2 sleep
            - 3 = N3 sleep
            - 4 = REM
    include : tuple, list or int
        Values in ``hypno`` that will be included in the mask. The default is
        (4), meaning that the detection is applied on REM sleep.
        This has no effect when ``hypno`` is None.
    amplitude : tuple or list
        Minimum and maximum amplitude of the peak of the REM.
        Default is 50 uV to 325 uV.
    duration : tuple or list
        The minimum and maximum duration of the REMs.
        Default is 0.3 to 1.2 seconds.
    freq_rem : tuple or list
        Frequency range of REMs. Default is 0.5 to 5 Hz.
    downsample : boolean
        If True, the data will be downsampled to 100 Hz or 128 Hz (depending
        on whether the original sampling frequency is a multiple of 100 or 128,
        respectively).
    remove_outliers : boolean
        If True, YASA will automatically detect and remove outliers REMs
        using :py:class:`sklearn.ensemble.IsolationForest`.
        YASA uses a random seed (42) to ensure reproducible results.
        Note that this step will only be applied if there are more than
        100 detected REMs in the first place. Default to False.

    Returns
    -------
    df_rem : :py:class:`pandas.DataFrame`
        Ouput detection dataframe::

            'Start' : Start of each detected REM (in seconds of data)
            'Peak' : Location of the peak (in seconds of data)
            'End' : End time (in seconds)
            'Duration' : Duration (in seconds)
            'LOCAbsValPeak' : LOC absolute amplitude at REM peak (in uV)
            'ROCAbsValPeak' : ROC absolute amplitude at REM peak (in uV)
            'LOCAbsRiseSlope' : LOC absolute rise slope (in uV/s)
            'ROCAbsRiseSlope' : ROC absolute rise slope (in uV/s)
            'LOCAbsFallSlope' : LOC absolute fall slope (in uV/s)
            'ROCAbsFallSlope' : ROC absolute fall slope (in uV/s)
            'Stage' : Sleep stage (only if hypno was provided)

    Notes
    -----
    For better results, apply this detection only on artefact-free REM sleep.

    Note that all the output parameters are computed on the filtered LOC and
    ROC signals.

    For an example of how to run the detection, please refer to
    https://github.com/raphaelvallat/yasa/blob/master/notebooks/09_REMs_detection.ipynb
    """
    # Safety checks
    loc = np.squeeze(np.asarray(loc, dtype=np.float64))
    roc = np.squeeze(np.asarray(roc, dtype=np.float64))
    assert loc.ndim == 1, 'LOC must be 1D.'
    assert roc.ndim == 1, 'ROC must be 1D.'
    assert loc.size == roc.size, 'LOC and ROC must have the same size.'
    assert isinstance(downsample, bool), 'Downsample must be True or False.'
    freq_rem = sorted(freq_rem)
    duration = sorted(duration)
    amplitude = sorted(amplitude)

    # Hypno processing
    if hypno is not None:
        hypno = np.asarray(hypno, dtype=int)
        assert hypno.ndim == 1, 'Hypno must be one dimensional.'
        assert hypno.size == loc.size, 'Hypno must have same size as data.'
        unique_hypno = np.unique(hypno)
        logger.info('Number of unique values in hypno = %i', unique_hypno.size)
        # Check include
        assert include is not None, 'include cannot be None if hypno is given'
        include = np.atleast_1d(np.asarray(include))
        assert include.size >= 1, '`include` must have at least one element.'
        assert hypno.dtype.kind == include.dtype.kind, ('hypno and include '
                                                        'must have same dtype')
        if not np.in1d(hypno, include).any():
            logger.error('None of the stages specified in `include` '
                         'are present in hypno. Returning None.')
            return None

    # Check data amplitude
    # times = np.arange(data.size) / sf
    data = np.vstack((loc, roc))
    loc_trimstd = trimbothstd(loc, cut=0.10)
    roc_trimstd = trimbothstd(roc, cut=0.10)
    loc_ptp, roc_ptp = np.ptp(loc), np.ptp(roc)
    logger.info('Number of samples in data = %i', data.shape[1])
    logger.info('Original sampling frequency = %.2f Hz', sf)
    logger.info('Data duration = %.2f seconds', data.shape[1] / sf)
    logger.info('Trimmed standard deviation of LOC = %.4f uV', loc_trimstd)
    logger.info('Trimmed standard deviation of ROC = %.4f uV', roc_trimstd)
    logger.info('Peak-to-peak amplitude of LOC = %.4f uV', loc_ptp)
    logger.info('Peak-to-peak amplitude of ROC = %.4f uV', roc_ptp)
    if not(1 < loc_trimstd < 1e3 or 1 < loc_ptp < 1e6):
        logger.error('Wrong LOC amplitude. Unit must be uV. Returning None.')
        return None
    if not(1 < roc_trimstd < 1e3 or 1 < roc_ptp < 1e6):
        logger.error('Wrong ROC amplitude. Unit must be uV. Returning None.')
        return None

    # Check if we can downsample to 100 or 128 Hz
    if downsample is True and sf > 128:
        if sf % 100 == 0 or sf % 128 == 0:
            new_sf = 100 if sf % 100 == 0 else 128
            fac = int(sf / new_sf)
            sf = new_sf
            data = data[:, ::fac]
            logger.info('Downsampled data by a factor of %i', fac)
            if hypno is not None:
                hypno = hypno[::fac]
                assert hypno.size == data.shape[1]
        else:
            logger.warning("Cannot downsample if sf is not a mutiple of 100 "
                           "or 128. Skipping downsampling.")

    # Bandpass filter
    data = filter_data(data, sf, freq_rem[0], freq_rem[1], verbose=0)

    # Calculate the negative product of LOC and ROC, maximal during REM.
    negp = -data[0, :] * data[1, :]

    # Find peaks in data
    # - height: required height of peaks (min and max.)
    # - distance: required distance in samples between neighboring peaks.
    # - prominence: required prominence of peaks.
    # - wlen: limit search for bases to a specific window.
    hmin, hmax = amplitude[0]**2, amplitude[1]**2
    pks, pks_params = signal.find_peaks(negp, height=(hmin, hmax),
                                        distance=(duration[0] * sf),
                                        prominence=(0.8 * hmin),
                                        wlen=(duration[1] * sf))

    # Intersect with sleep stage vector
    # We do that before calculating the features in order to gain some time
    if hypno is not None:
        mask = np.in1d(hypno, include)
        idx_mask = np.where(mask)[0]
        pks, idx_good, _ = np.intersect1d(pks, idx_mask, True, True)
        for k in pks_params.keys():
            pks_params[k] = pks_params[k][idx_good]

    # If no peaks are detected, return None
    if len(pks) == 0:
        logger.warning('No REMs were found in data. Returning None.')
        return None

    # Hypnogram
    if hypno is not None:
        # The sleep stage at the beginning of the REM is considered.
        rem_sta = hypno[pks_params['left_bases']]
    else:
        rem_sta = np.zeros(pks.shape)

    # Calculate time features
    pks_params['Start'] = pks_params['left_bases'] / sf
    pks_params['Peak'] = pks / sf
    pks_params['End'] = pks_params['right_bases'] / sf
    pks_params['Duration'] = pks_params['End'] - pks_params['Start']
    # Time points in minutes (HH:MM:SS)
    # pks_params['StartMin'] = pd.to_timedelta(pks_params['Start'], unit='s').dt.round('s')  # noqa
    # pks_params['PeakMin'] = pd.to_timedelta(pks_params['Peak'], unit='s').dt.round('s')  # noqa
    # pks_params['EndMin'] = pd.to_timedelta(pks_params['End'], unit='s').dt.round('s')  # noqa
    # Absolute LOC / ROC value at peak (filtered)
    pks_params['LOCAbsValPeak'] = abs(data[0, pks])
    pks_params['ROCAbsValPeak'] = abs(data[1, pks])
    # Absolute rising and falling slope
    dist_pk_left = (pks - pks_params['left_bases']) / sf
    dist_pk_right = (pks_params['right_bases'] - pks) / sf
    locrs = (data[0, pks] - data[0, pks_params['left_bases']]) / dist_pk_left
    rocrs = (data[1, pks] - data[1, pks_params['left_bases']]) / dist_pk_left
    locfs = (data[0, pks_params['right_bases']] - data[0, pks]) / dist_pk_right
    rocfs = (data[1, pks_params['right_bases']] - data[1, pks]) / dist_pk_right
    pks_params['LOCAbsRiseSlope'] = abs(locrs)
    pks_params['ROCAbsRiseSlope'] = abs(rocrs)
    pks_params['LOCAbsFallSlope'] = abs(locfs)
    pks_params['ROCAbsFallSlope'] = abs(rocfs)
    # Sleep stage
    pks_params['Stage'] = rem_sta

    # Convert to Pandas DataFrame
    df_rem = pd.DataFrame(pks_params)

    # Make sure that the sign of ROC and LOC is opposite
    df_rem['IsOppositeSign'] = np.sign(data[1, pks]) != np.sign(data[0, pks])
    df_rem = df_rem[np.sign(data[1, pks]) != np.sign(data[0, pks])]

    # Remove bad duration
    tmin, tmax = duration
    good_dur = np.logical_and(pks_params['Duration'] >= tmin,
                              pks_params['Duration'] < tmax)
    df_rem = df_rem[good_dur]

    # Keep only useful channels
    df_rem = df_rem[['Start', 'Peak', 'End', 'Duration', 'LOCAbsValPeak',
                     'ROCAbsValPeak', 'LOCAbsRiseSlope', 'ROCAbsRiseSlope',
                     'LOCAbsFallSlope', 'ROCAbsFallSlope', 'Stage']]

    if hypno is None:
        df_rem = df_rem.drop(columns=['Stage'])
    else:
        df_rem['Stage'] = df_rem['Stage'].astype(int).astype('category')

    # We need at least 100 detected REMs to apply the Isolation Forest.
    if remove_outliers and df_rem.shape[0] >= 100:
        from sklearn.ensemble import IsolationForest
        col_keep = ['Duration', 'LOCAbsValPeak', 'ROCAbsValPeak',
                    'LOCAbsRiseSlope', 'ROCAbsRiseSlope', 'LOCAbsFallSlope',
                    'ROCAbsFallSlope']
        ilf = IsolationForest(behaviour='new', contamination='auto',
                              max_samples='auto', verbose=0, random_state=42)
        good = ilf.fit_predict(df_rem[col_keep])
        good[good == -1] = 0
        logger.info('%i outliers were removed.', (good == 0).sum())
        # Remove outliers from DataFrame
        df_rem = df_rem[good.astype(bool)]

    logger.info('%i REMs were found in data.', df_rem.shape[0])
    return df_rem.reset_index(drop=True)
