from datetime import datetime

def process_signal(payload):
    return {
        "asset": payload["asset"],
        "point": payload["point"],

        "health_index": 0.85,
        "condition": "NORMAL",

        "velocity": {
            "rms_mm_s": 2.1,
            "iso_zone": "B"
        },

        "bearing": {
            "env_kurtosis": 3.2,
            "energy_ratio": 0.25
        },

        "harmonics": {
            "1x_g": 0.12,
            "2x_g": 0.05,
            "3x_g": 0.03
        },

        "timestamp": datetime.now().isoformat()
    }

