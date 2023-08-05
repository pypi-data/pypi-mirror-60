# - * - coding: utf-8 - * -

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal

from .ecg_findpeaks import ecg_findpeaks
from .ecg_fixpeaks import ecg_fixpeaks
from ..signal import signal_formatpeaks


def ecg_peaks(ecg_cleaned, sampling_rate=1000, method="neurokit", show=False):
    """Find R-peaks in an ECG signal.

    Find R-peaks in an ECG signal using the specified method.

    Parameters
    ----------
    ecg_cleaned : list, array or Series
        The cleaned ECG channel as returned by `ecg_clean()`.
    sampling_rate : int
        The sampling frequency of `ecg_signal` (in Hz, i.e., samples/second).
        Defaults to 1000.
    method : string
        The algorithm to be used for R-peak detection. Can be one of 'neurokit' (default),
        'pamtompkins1985', 'hamilton2002', 'christov2004', 'gamboa2008', 'elgendi2010',
        'engzeemod2012' or 'kalidas2017'.
    show : bool
        If True, will return a plot to visualizing the thresholds used in the
        algorithm. Useful for debugging.

    Returns
    -------
    signals : DataFrame
        A DataFrame of same length as the input signal in which occurences of
        R-peaks marked as "1" in a list of zeros with the same length as
        `ecg_cleaned`. Accessible with the keys "ECG_R_Peaks".
    info : dict
        A dictionary containing additional information, in this case the
        samples at which R-peaks occur, accessible with the key "ECG_R_Peaks".

    See Also
    --------
    ecg_clean, ecg_findpeaks, ecg_fixpeaks, ecg_rate, ecg_process, ecg_plot

    Examples
    --------
    >>> import neurokit2 as nk
    >>>
    >>> ecg = nk.ecg_simulate(duration=10, sampling_rate=1000)
    >>> cleaned = nk.ecg_clean(ecg, sampling_rate=1000)
    >>> peak_signal, info = nk.ecg_peaks(cleaned)
    >>> nk.events_plot(info["ECG_R_Peaks"], cleaned)

    References
    --------------
    - Gamboa, H. (2008). Multi-modal behavioral biometrics based on hci and electrophysiology. PhD ThesisUniversidade.
    - W. Zong, T. Heldt, G.B. Moody, and R.G. Mark. An open-source algorithm to detect onset of arterial blood pressure pulses. In Computers in Cardiology, 2003, pages 259–262, 2003.
    - Hamilton, Open Source ECG Analysis Software Documentation, E.P.Limited, 2002.
    - Jiapu Pan and Willis J. Tompkins. A Real-Time QRS Detection Algorithm. In: IEEE Transactions on Biomedical Engineering BME-32.3 (1985), pp. 230–236.
    - C. Zeelenberg, A single scan algorithm for QRS detection and feature extraction, IEEE Comp. in Cardiology, vol. 6, pp. 37-42, 1979
    - A. Lourenco, H. Silva, P. Leite, R. Lourenco and A. Fred, "Real Time Electrocardiogram Segmentation for Finger Based ECG Biometrics", BIOSIGNALS 2012, pp. 49-54, 2012.
    """
    info = ecg_findpeaks(ecg_cleaned, sampling_rate=sampling_rate, method=method)
    info = ecg_fixpeaks(info, sampling_rate=sampling_rate)
    peak_signal = signal_formatpeaks(info,
                                     desired_length=len(ecg_cleaned),
                                     peak_indices=info["ECG_R_Peaks"])

    return peak_signal, info
