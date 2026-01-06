def health_index(features):
    # contoh sederhana
    rms = features.get("rms", 0)
    kurt = features.get("kurtosis", 3)

    hi = max(0.0, min(1.0, 1 - (rms * 10 + abs(kurt - 3) * 0.1)))
    return hi

