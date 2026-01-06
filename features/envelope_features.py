import numpy as np
from scipy.signal import butter, filtfilt, hilbert

def envelope_features(signal, fs, hf_band):
    low, high = hf_band
    b, a = butter(4, [low/(fs/2), high/(fs/2)], btype="band")
    hf = filtfilt(b, a, signal)

    env = np.abs(hilbert(hf))
    rms = np.sqrt(np.mean(env**2))
    kurt = np.mean((env - env.mean())**4) / (env.std()**4)

    return rms, kurt
