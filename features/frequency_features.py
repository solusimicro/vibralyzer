import numpy as np

def frequency_features(signal, fs, band):
    features = {}

    signal = np.asarray(signal)

    # ✅ REMOVE MEAN (PENTING)
    signal = signal - np.mean(signal)

    # ✅ WINDOWING (industrial standard)
    window = np.hanning(len(signal))
    signal = signal * window

    spectrum = np.abs(np.fft.rfft(signal)) ** 2
    freqs = np.fft.rfftfreq(len(signal), d=1/fs)

    spectrum[0] = 0.0
    total_energy = np.sum(spectrum)

    for name, (f1, f2) in band.items():
        idx = (freqs >= f1) & (freqs < f2)
        band_energy = np.sum(spectrum[idx])
        features[f"{name}_energy_ratio"] = (
            band_energy / total_energy if total_energy > 0 else 0.0
        )

    if spectrum.max() < 1e-10:
        features["dominant_freq"] = 0.0
    else:
        features["dominant_freq"] = freqs[np.argmax(spectrum)]

    return features

    # fitur tambahan bisa ditambahkan di sini