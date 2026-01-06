def machine_status(features):
    hi = features.get("health_index", 1)
    rms = features.get("rms", 0)
    kurt = features.get("kurtosis", 0)

    if hi < 0.6 or kurt > 4:
        return "ALARM"
    if hi < 0.8 or kurt > 3:
        return "WARNING"
    return "NORMAL"
