import json
import time
import numpy as np
import paho.mqtt.publish as publish
from datetime import datetime, timezone

BROKER = "localhost"
FS = 25600
WINDOW = 4096

# ============================================================
# MACHINE CONFIG (LOCKED v1.0.0)
# ============================================================
MACHINES = {
    "PUMP_01": {
        "rpm": 1480,
        "bpfo": 92,
        "base_temp": 42.0,
        "points": [
            "1P.MT",
            "2P.MT",
            "3P.GX",
            "4P.GX",
            "5P.GX",
            "6P.GX",
            "7P.PP",
            "8P.PP",
        ],
    }
}

HF_RESONANCE = 8000  # Hz

# ============================================================
# TEMPERATURE STATE (per asset)
# ============================================================
TEMP_STATE = {
    asset: cfg["base_temp"]
    for asset, cfg in MACHINES.items()
}

# ============================================================
# SIGNAL GENERATOR
# ============================================================
def generate_bearing_fault_signal(n, fs, rpm, bpfo, gain=1.0):
    t = np.arange(n) / fs
    fr = rpm / 60.0

    base = 0.02 * np.sin(2 * np.pi * fr * t)
    hf = np.sin(2 * np.pi * HF_RESONANCE * t)

    impulse_interval = int(fs / bpfo) if bpfo > 0 else n
    impulses = np.zeros(n)
    impulses[::impulse_interval] = 1.0

    bearing = gain * 0.15 * impulses * hf
    noise = 0.003 * np.random.randn(n)

    return (base + bearing + noise).tolist()

# ============================================================
# TEMPERATURE MODEL
# ============================================================
def update_temperature(asset, severity=1.0):
    temp = TEMP_STATE[asset]

    # natural drift
    temp += np.random.normal(0, 0.05)

    # fault heating
    temp += 0.12 * severity

    # clamp realistic
    temp = max(25.0, min(temp, 110.0))

    TEMP_STATE[asset] = temp
    return round(temp, 2)

# ============================================================
# PUBLISH LOOP
# ============================================================
def send_signals():
    for asset, cfg in MACHINES.items():
        rpm = cfg["rpm"]
        bpfo = cfg["bpfo"]

        # shared asset temperature
        base_temp = update_temperature(asset, severity=1.0)

        for idx, point in enumerate(cfg["points"]):
            # small variation per point
            point_gain = 1.0 + (idx * 0.05)
            point_temp = round(base_temp + np.random.normal(0, 0.3), 2)

            signal = generate_bearing_fault_signal(
                n=WINDOW,
                fs=FS,
                rpm=rpm,
                bpfo=bpfo,
                gain=point_gain,
            )

            payload = {
                "schema_version": "1.1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "asset": asset,
                "point": point,
                "fs": FS,
                "rpm": rpm,
                "temperature_c": point_temp,
                "acceleration_g": signal,
            }

            topic = f"vibration/raw/{asset}/{point}"

            publish.single(
                topic=topic,
                payload=json.dumps(payload),
                hostname=BROKER,
                qos=1,
            )

            print(
                f"📡 {asset} | {point} | "
                f"T={point_temp}°C | RPM={rpm}"
            )

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    while True:
        send_signals()
        time.sleep(1)
