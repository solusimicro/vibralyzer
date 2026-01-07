from utils.logger import get_logger

logger = get_logger("fault_diagnostic")

def detect_fault_with_confidence(features):
    faults = []

    # =========================
    # BEARING FAULT
    # =========================
    if (
        features.get("bearing_energy_ratio", 0) > 0.35 and
        features.get("env_kurtosis", 0) > 3.5 and
        features.get("env_rms", 0) > 1.2 * features.get("baseline_env_rms", 1)
    ):
        confidence = min(
            1.0,
            features["bearing_energy_ratio"]
        )
        faults.append({
            "fault": "BEARING_DEFECT",
            "confidence": round(confidence, 2)
        })

    # =========================
    # IMBALANCE
    # =========================
    if (
        abs(features.get("dominant_freq", 0) - features.get("rpm", 0)/60) < 0.5 and
        features.get("rms", 0) > 1.5 * features.get("baseline_rms", 1)
    ):
        faults.append({
            "fault": "IMBALANCE",
            "confidence": 0.7
        })

    # =========================
    # MISALIGNMENT
    # =========================
    if (
        features.get("order_2x", 0) > features.get("order_1x", 0) * 0.6
    ):
        faults.append({
            "fault": "MISALIGNMENT",
            "confidence": 0.6
        })

    return faults

