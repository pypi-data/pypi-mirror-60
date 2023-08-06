"""
This file contains several helper functions to calculate sleep statistics from
a one-dimensional sleep staging vector (hypnogram).
"""
import numpy as np
import pandas as pd

__all__ = ['transition_matrix', 'sleep_statistics']


#############################################################################
# TRANSITION MATRIX
#############################################################################

def transition_matrix(hypno):
    """Create a state-transition matrix from an hypnogram.

    .. versionadded:: 0.1.9

    Parameters
    ----------
    hypno : array_like
        Hypnogram. The dtype of ``hypno`` must be integer
        (e.g. [0, 2, 2, 1, 1, 1, ...]). The sampling frequency must be the
        original one, i.e. 1 value per 30 seconds if the staging was done in
        30 seconds epochs. Using an upsampled hypnogram will result in an
        incorrect transition matrix.
        For best results, we recommend using an hypnogram cropped to
        either the time in bed (TIB) or the sleep period time (SPT).

    Returns
    -------
    counts : array
        Counts transition matrix (number of transitions from stage X to
        stage Y).
    probs : array
        Conditional probability transition matrix, i.e.
        given that current state is X, what is the probability that
        the next state is Y.
        ``probs`` is a right stochastic matrix, i.e. each row sums to 1.
        See more details at:
        https://en.wikipedia.org/wiki/Stochastic_matrix

    Examples
    --------
    >>> from yasa import transition_matrix
    >>> a = [1, 1, 1, 0, 0, 2, 2, 0, 2, 0, 1, 1, 0, 0]
    >>> counts, probs = transition_matrix(a)
    >>> counts
           0  1  2
    Stage
    0      2  1  2
    1      2  3  0
    2      2  0  1

    >>> probs
                  0    1         2
    Stage
    0      0.400000  0.2  0.400000
    1      0.400000  0.6  0.000000
    2      0.666667  0.0  0.333333
    """
    x = np.asarray(hypno, dtype=int)
    unique, inverse = np.unique(x, return_inverse=True)
    n = unique.size
    # Integer transition counts
    counts = np.zeros((n, n), dtype=int)
    np.add.at(counts, (inverse[:-1], inverse[1:]), 1)
    # Conditional probabilities
    probs = counts / counts.sum(axis=-1, keepdims=True)
    # Optional, convert to Pandas
    counts = pd.DataFrame(counts, index=unique, columns=unique)
    probs = pd.DataFrame(probs, index=unique, columns=unique)
    counts.index.name = 'Stage'
    probs.index.name = 'Stage'
    return counts, probs

#############################################################################
# SLEEP STATISTICS
#############################################################################


def sleep_statistics(hypno, sf_hyp):
    """Compute sleep stats from an hypnogram vector.

    .. versionadded:: 0.1.9

    Parameters
    ----------
    hypno : array_like
        Hypnogram vector, assumed to be already cropped to time in bed (TIB).

        .. note::
            The default hypnogram format in YASA is a 1D integer
            vector where:

            - -1 = Artefact / Movement
            - 0 = Wake
            - 1 = N1 sleep
            - 2 = N2 sleep
            - 3 = N3 sleep
            - 4 = REM sleep
    sf_hyp : float
        The sampling frequency of the hypnogram. Should be 1/30 if there is one
        value per 30-seconds, 1/20 if there is one value per 20-seconds,
        1 if there is one value per second, and so on.

    Returns
    -------
    stats: dict
        Sleep statistics (expressed in minutes)

    Notes
    -----
    All values except SE and percentages are expressed in minutes.

    * Time in Bed (TIB): total duration of the hypnogram.
    * Sleep Period Time (SPT): duration from first to last period of sleep.
    * Wake After Sleep Onset (WASO): duration of wake periods within SPT.
    * Total Sleep Time (TST): SPT - WASO.
    * Sleep Efficiency (SE): TST / SPT * 100 (%).
    * W, N1, N2, N3 and REM: sleep stages duration. NREM = N1 + N2 + N3.
    * % (W, ... REM): sleep stages duration expressed in percentages of TST.
    * Latencies: latencies of sleep stages from the beginning of the record.

    Examples
    --------
    >>> from yasa import sleep_statistics
    >>> hypno = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 2, 3, 3, 4, 4, 4, 4, 0, 0]
    >>> # Assuming that we have one-value per 30-second.
    >>> sleep_statistics(hypno, sf_hyp=1/30)
    {'TIB': 10.0,
     'N1': 1.5,
     'N2': 2.0,
     'N3': 2.5,
     'REM': 2.0,
     'NREM': 6.0,
     'Lat_N1': 1.0,
     'Lat_N2': 2.5,
     'Lat_N3': 4.0,
     'Lat_REM': 7.0,
     'SPT': 8.0,
     'WASO': 0.0,
     'TST': 8.0,
     '%N1': 18.75,
     '%N2': 25.0,
     '%N3': 31.25,
     '%REM': 25.0,
     '%NREM': 75.0,
     'SE': 100.0}
    """
    stats = {}
    hypno = np.asarray(hypno)
    assert hypno.ndim == 1, 'hypno must have only one dimension.'
    assert hypno.size > 1, 'hypno must have at least two elements.'

    # TIB, first and last sleep
    stats['TIB'] = len(hypno)
    first_sleep = np.where(hypno > 0)[0][0]
    last_sleep = np.where(hypno > 0)[0][-1]

    # Duration of each sleep stages
    stats['N1'] = hypno[hypno == 1].size
    stats['N2'] = hypno[hypno == 2].size
    stats['N3'] = hypno[hypno == 3].size
    stats['REM'] = hypno[hypno == 4].size
    stats['NREM'] = stats['N1'] + stats['N2'] + stats['N3']

    # Sleep stage latencies
    stats['Lat_N1'] = np.where(hypno == 1)[0].min() if 1 in hypno else np.nan
    stats['Lat_N2'] = np.where(hypno == 2)[0].min() if 2 in hypno else np.nan
    stats['Lat_N3'] = np.where(hypno == 3)[0].min() if 3 in hypno else np.nan
    stats['Lat_REM'] = np.where(hypno == 4)[0].min() if 4 in hypno else np.nan

    # Crop to SPT
    hypno_s = hypno[first_sleep:(last_sleep + 1)]
    stats['SPT'] = hypno_s.size
    stats['WASO'] = hypno_s[hypno_s == 0].size
    stats['TST'] = stats['SPT'] - stats['WASO']

    # Convert to minutes
    for key, value in stats.items():
        stats[key] = value / (60 * sf_hyp)

    # Percentage
    stats['%N1'] = 100 * stats['N1'] / stats['TST']
    stats['%N2'] = 100 * stats['N2'] / stats['TST']
    stats['%N3'] = 100 * stats['N3'] / stats['TST']
    stats['%REM'] = 100 * stats['REM'] / stats['TST']
    stats['%NREM'] = 100 * stats['NREM'] / stats['TST']
    stats['SE'] = 100 * stats['TST'] / stats['SPT']
    return stats
