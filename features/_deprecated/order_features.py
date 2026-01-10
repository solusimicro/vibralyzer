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

WINDOW_CORR = 2.0  # amplitude correction for Hanning (FFT domain)

def order_amplitude(freqs, spectrum, rpm, order, bw=0.03):
    order_freq = order * rpm / 60.0

    idx = np.where(
        (freqs >= order_freq * (1 - bw)) &
        (freqs <= order_freq * (1 + bw))
    )[0]

    if len(idx) == 0:
        return 0.0

    return float(np.sqrt(np.max(spectrum[idx])) * WINDOW_CORR)

def order_features(signal, fs, rpm):
    signal = np.asarray(signal)
    n = len(signal)

    spectrum = np.abs(np.fft.rfft(signal))**2
    freqs = np.fft.rfftfreq(n, 1/fs)

    return {
        "order_1x": order_amplitude(freqs, spectrum, rpm, 1),
        "order_2x": order_amplitude(freqs, spectrum, rpm, 2),
        "order_3x": order_amplitude(freqs, spectrum, rpm, 3)
    }

