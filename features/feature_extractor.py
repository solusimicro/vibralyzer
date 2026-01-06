from datetime import datetime

def process_signal(payload, features):
    return {
        "asset": payload["asset"],
        "point": payload["point"],

        "health_index": features["health_index"],
        "condition": features["machine_status"],

        "velocity": {
            "rms_mm_s": features["velocity_rms_mm_s"],
            "iso_zone": features["iso_zone"]
        },

        "bearing": {
            "env_kurtosis": features.get("env_kurtosis"),
            "energy_ratio": features.get("hf_energy_ratio")
        },

        "harmonics": {
            "1x_g": features.get("order_1x"),
            "2x_g": features.get("order_2x"),
            "3x_g": features.get("order_3x")
        },

        "timestamp": datetime.now().isoformat()
    }
