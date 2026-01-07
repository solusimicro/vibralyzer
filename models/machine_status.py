def machine_status(features, faults):
    hi = features.get("health_index", 1)

    if any(f["confidence"] > 0.8 for f in faults):
        return "ALARM"

    if hi < 0.8 or faults:
        return "WARNING"

    return "NORMAL"

