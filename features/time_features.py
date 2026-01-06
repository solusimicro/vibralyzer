import numpy as np

# Hanning window amplitude compensation factor
WINDOW_CORR = np.sqrt(8 / 3)  # ≈ 1.633

def time_features(signal):
    signal = np.asarray(signal)

    mean = np.mean(signal)
    std = np.std(signal)

    # proteksi division by zero
    if std == 0:
        std = 1e-12

    rms = np.sqrt(np.mean(signal**2)) * WINDOW_CORR
    peak = np.max(np.abs(signal)) * WINDOW_CORR

    kurtosis = np.mean((signal - mean)**4) / (std**4)
    skewness = np.mean((signal - mean)**3) / (std**3)

    return {
        "rms": float(rms),
        "peak": float(peak),
        "kurtosis": float(kurtosis),
        "skewness": float(skewness)
    }
