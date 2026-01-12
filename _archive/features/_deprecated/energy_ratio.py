"""
DEPRECATED MODULE
-----------------
DO NOT USE IN PRODUCTION.

This module is kept for:
- reference
- experiment
- backward traceability

All production features are calculated in:
core/feature_pipeline.py
"""

import numpy as np
from scipy.signal import butter, filtfilt

def band_rms(signal, fs, band):
    b, a = butter(4, [band[0]/(fs/2), band[1]/(fs/2)], btype="band")
    s = filtfilt(b, a, signal)
    return np.sqrt(np.mean(s**2))

def bearing_energy_ratio(signal, fs, bands):
    hf = band_rms(signal, fs, bands['hf'])
    overall = np.sqrt(np.mean(signal**2))
    return hf / overall if overall > 0 else 0
