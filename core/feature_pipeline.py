# ============================================================
# FEATURE PIPELINE – PREVENTIVE MAINTENANCE VIBRATION
# + ISO ZONE (ISO 20816)
# ============================================================

import numpy as np
from scipy.signal import butter, filtfilt, hilbert

from models.fault_diagnostic import detect_fault_with_confidence
from models.fault_persistence import FaultPersistence
from models.maintenance_recommendation import generate_recommendation
from core.scada_publisher import publish_scada_features


# ============================================================
# UTIL
# ============================================================
def rms(x):
    return np.sqrt(np.mean(x ** 2)) if len(x) > 0 else 0.0


# ============================================================
# FEATURE FUNCTIONS
# ============================================================
def time_domain_features(signal):
    signal = np.asarray(signal)
    rms_val = rms(signal)
    peak = np.max(np.abs(signal)) if rms_val > 0 else 0.0
    return {
        "crest_factor": float(peak / rms_val) if rms_val > 0 else 0.0
    }


def acc_hf_rms(signal, fs, band=(3000, 10000)):
    b, a = butter(4, [band[0] / (fs / 2), band[1] / (fs / 2)], btype="band")
    return float(rms(filtfilt(b, a, signal)))


def envelope_features(signal, fs, band=(3000, 10000)):
    b, a = butter(4, [band[0] / (fs / 2), band[1] / (fs / 2)], btype="band")
    env = np.abs(hilbert(filtfilt(b, a, signal)))
    std = np.std(env)
    kurt = np.mean((env - env.mean()) ** 4) / (std ** 4) if std > 0 else 0.0
    return {
        "envelope_rms": float(rms(env)),
        "envelope_kurtosis": float(kurt)
    }


def frequency_features(signal, fs, band=(3000, 10000)):
    signal = signal - np.mean(signal)
    spec = np.abs(np.fft.rfft(signal * np.hanning(len(signal)))) ** 2
    freqs = np.fft.rfftfreq(len(signal), 1 / fs)

    total_energy = np.sum(spec)
    idx = (freqs >= band[0]) & (freqs <= band[1])
    ratio = np.sum(spec[idx]) / total_energy if total_energy > 0 else 0.0

    psd = spec / np.sum(spec) if np.sum(spec) > 0 else spec
    entropy = -np.sum(psd * np.log2(psd + 1e-12))

    return {
        "bearing_energy_ratio": float(ratio),
        "spectral_entropy": float(entropy)
    }


def order_features(signal, fs, rpm, bw=0.03):
    if rpm is None or rpm <= 0:
        return {"1x_order_amp": 0.0, "2x_order_ratio": 0.0}

    signal = signal - np.mean(signal)
    spec = np.abs(np.fft.rfft(signal * np.hanning(len(signal)))) ** 2
    freqs = np.fft.rfftfreq(len(signal), 1 / fs)

    def get(order):
        f0 = order * rpm / 60
        idx = (freqs >= f0 * (1 - bw)) & (freqs <= f0 * (1 + bw))
        return np.sqrt(np.max(spec[idx])) if np.any(idx) else 0.0

    a1 = get(1)
    a2 = get(2)

    return {
        "1x_order_amp": float(a1),
        "2x_order_ratio": float(a2 / a1) if a1 > 0 else 0.0
    }


# ============================================================
# ISO ZONE (ISO 20816 – GENERAL MACHINERY)
# ============================================================
def overall_velocity_rms_mm_s(signal, fs):
    # signal diasumsikan acceleration (g)
    acc_ms2 = np.asarray(signal) * 9.81
    vel = np.cumsum(acc_ms2) / fs
    return float(rms(vel) * 1000)  # mm/s


def iso_zone(vel_rms):
    if vel_rms < 1.8:
        return "A", 0
    elif vel_rms < 4.5:
        return "B", 0
    elif vel_rms < 7.1:
        return "C", 1
    else:
        return "D", 2


# ============================================================
# PIPELINE CLASS
# ============================================================
class FeaturePipeline:

    def __init__(self):
        self.persistence = FaultPersistence(window=5)

    def process(self, signal, fs, asset, point, rpm=None):

        # =====================================================
        # 1️⃣ FEATURE EXTRACTION
        # =====================================================
        features = {
            "acc_hf_rms_g": acc_hf_rms(signal, fs),
            **time_domain_features(signal),
            **envelope_features(signal, fs),
            **frequency_features(signal, fs),
            **order_features(signal, fs, rpm)
        }

        # ISO velocity
        vel_rms = overall_velocity_rms_mm_s(signal, fs)
        zone, zone_code = iso_zone(vel_rms)

        features["overall_vel_rms_mm_s"] = vel_rms

        # =====================================================
        # 2️⃣ ALARM STATUS & HEALTH
        # =====================================================
        if features["acc_hf_rms_g"] >= 0.6:
            alarm_status = "ALARM"
        elif features["acc_hf_rms_g"] >= 0.3:
            alarm_status = "WARNING"
        else:
            alarm_status = "NORMAL"

        health_score = max(0.0, 100.0 - features["acc_hf_rms_g"] * 100.0)

        # =====================================================
        # 3️⃣ FAULT DIAGNOSTIC + PERSISTENCE
        # =====================================================
        raw_faults = detect_fault_with_confidence(features)

        persistent_faults = self.persistence.update(
            asset=asset,
            point=point,
            faults=raw_faults
        ) or []

        recommendation = generate_recommendation(persistent_faults) if persistent_faults else None

        # =====================================================
        # 4️⃣ CONTEXT
        # =====================================================
        context = {
            "alarm_status": alarm_status,
            "health_score": health_score,
            "fault_candidates": persistent_faults,
            "iso_zone": zone,
            "iso_zone_code": zone_code
        }

        # =====================================================
        # 5️⃣ FINAL ALARM CODE
        # =====================================================
        alarm_code = 0

        if any(f.get("severity") in ("HIGH", "CRITICAL") for f in persistent_faults):
            alarm_code = 2
        elif persistent_faults:
            alarm_code = 1

        # ISO SAFETY OVERRIDE
        if zone_code == 2:
            alarm_code = max(alarm_code, 2)

        # =====================================================
        # 6️⃣ PUBLISH (FINAL)
        # =====================================================
        publish_scada_features(
            asset=asset,
            point=point,
            rpm=rpm,
            features=features,
            context=context,
            alarm_code=alarm_code,
            recommendation=recommendation
        )


