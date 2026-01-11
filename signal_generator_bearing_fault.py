import json
import time
import numpy as np
import paho.mqtt.publish as publish
from datetime import datetime, timezone

BROKER = "localhost"
FS = 25600

# ==========================
# Machine info
# ==========================
MACHINES = {
    "PUMP_01": {"rpm": 1480, "point": "DE", "bpfo": 92},
    "PUMP_02": {"rpm": 2960, "point": "DE", "bpfo": 184}
}

HF_RESONANCE = 8000  # Hz (typical bearing resonance)

# ==========================
# Generate bearing fault signal
# ==========================
def generate_bearing_fault_signal(n=4096, fs=FS, rpm=0, bpfo=1):
    t = np.arange(n) / fs
    FR = rpm / 60

    # base 1X
    base = 0.02 * np.sin(2 * np.pi * FR * t)

    # HF carrier
    hf_carrier = np.sin(2 * np.pi * HF_RESONANCE * t)

    # Impulse train
    impulse_interval = int(fs / bpfo) if bpfo > 0 else n
    impulses = np.zeros(n)
    impulses[::impulse_interval] = 1.0

    # Modulated HF bursts
    bearing_fault = 0.15 * impulses * hf_carrier

    # Noise
    noise = 0.003 * np.random.randn(n)

    signal = base + bearing_fault + noise
    return signal.tolist()

# ==========================
# Send signal via MQTT
# ==========================
def send_signals():
    for asset, info in MACHINES.items():
        signal_data = generate_bearing_fault_signal(
            n=4096, fs=FS, rpm=info["rpm"], bpfo=info["bpfo"]
        )

        payload = {
            "schema_version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "asset": asset,                  # wajib ada
            "point": info["point"],          # wajib ada
            "fs": FS,
            "rpm": info["rpm"],
            "acceleration_g": signal_data
        }

        topic = f"vibration/raw/{asset}/{info['point']}"

        publish.single(
            topic=topic,
            payload=json.dumps(payload),
            hostname=BROKER,
            qos=1
        )

        print(f"✅ FAULT PUBLISHED | ASSET={asset} | POINT={info['point']} | TS={payload['timestamp']}")

# ==========================
# Main loop
# ==========================
if __name__ == "__main__":
    while True:
        send_signals()
        time.sleep(1)


