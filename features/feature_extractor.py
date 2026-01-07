from datetime import datetime
import math
from models.health_index import health_index
from models.machine_status import machine_status

# ===== Helper =====
def safe_float(value, default=0.0):
    """Pastikan value bisa dikonversi ke float, kalau None pakai default"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# ===== ISO Zone =====
def iso_zone_from_velocity(vel_mm_s):
    if vel_mm_s < 1.8:
        return "A"
    elif vel_mm_s < 4.5:
        return "B"
    elif vel_mm_s < 7.1:
        return "C"
    else:
        return "D"

def iso_zone_from_acc(acc_rms_g, dominant_freq_hz):
    if dominant_freq_hz <= 0:
        return "UNKNOWN"
    acc_ms2 = acc_rms_g * 9.81
    vel_ms = acc_ms2 / (2 * math.pi * dominant_freq_hz)
    vel_mm_s = vel_ms * 1000
    return iso_zone_from_velocity(vel_mm_s)

# ===== Processor =====
def process_signal(payload, features):
    """
    Format fitur mentah menjadi JSON payload siap publish
    Aman untuk nilai None
    """
    # ==== Ambil velocity RMS dengan default 0.0 ====
    vel_rms = safe_float(features.get("velocity_rms_mm_s"))

    # ==== Hitung ISO zone ====
    if vel_rms > 0:
        iso_zone_val = iso_zone_from_velocity(vel_rms)
    elif "acc_rms_g" in features and "dominant_freq" in features:
        acc_rms = safe_float(features.get("acc_rms_g"))
        dominant_freq = safe_float(features.get("dominant_freq"))
        iso_zone_val = iso_zone_from_acc(acc_rms, dominant_freq)
    else:
        iso_zone_val = "UNKNOWN"

    # ==== Health & Status ====
    try:
        hi = health_index(features)
    except Exception:
        hi = 0.0

    try:
        status = machine_status(features)
    except Exception:
        status = "UNKNOWN"

    return {
        "asset": payload.get("asset"),
        "point": payload.get("point"),
        "health_index": hi,
        "condition": status,
        "velocity": {
            "rms_mm_s": vel_rms,
            "iso_zone": iso_zone_val
        },
        "bearing": {
            "env_kurtosis": safe_float(features.get("env_kurtosis")),
            "energy_ratio": safe_float(features.get("hf_energy_ratio"))
        },
        "harmonics": {
            "1x_g": safe_float(features.get("order_1x")),
            "2x_g": safe_float(features.get("order_2x")),
            "3x_g": safe_float(features.get("order_3x"))
        },
        "timestamp": datetime.now().isoformat()
    }
