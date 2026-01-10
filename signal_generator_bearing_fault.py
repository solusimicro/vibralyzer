# signal_generator_bearing_fault.py
import json
import time
import numpy as np
import paho.mqtt.publish as publish
from datetime import datetime, timezone

BROKER = "localhost"
TOPIC = "vibration/raw/PUMP_01/DE"

FS = 25600
RPM = 2880
FR = RPM / 60           # running frequency (Hz)

# Simulasi BPFO (contoh)
BPFO = 4.2 * FR         # bearing outer race characteristic freq
HF_RESONANCE = 8000     # Hz (typical bearing resonance)


def generate_bearing_fault_signal(n=4096, fs=FS):
    t = np.arange(n) / fs

    # 1️⃣ Fundamental (1X)
    base = 0.02 * np.sin(2 * np.pi * FR * t)

    # 2️⃣ HF resonance carrier
    hf_carrier = np.sin(2 * np.pi * HF_RESONANCE * t)

    # 3️⃣ Impulse train (bearing defect)
    impulse_interval = int(fs / BPFO)
    impulses = np.zeros(n)
    impulses[::impulse_interval] = 1.0

    # 4️⃣ Modulated HF bursts
    bearing_fault = 0.15 * impulses * hf_carrier

    # 5️⃣ Noise
    noise = 0.003 * np.random.randn(n)

    signal = base + bearing_fault + noise
    return signal.tolist()


def send_signal():
    signal_data = generate_bearing_fault_signal()

    payload = {
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "asset": "PUMP_01",
        "point": "DE",

        "fs": FS,
        "rpm": RPM,

        "signal": signal_data
    }

    publish.single(
        topic=TOPIC,
        payload=json.dumps(payload),
        hostname=BROKER,
        qos=1
    )

    print(
        f"FAULT PUBLISHED | "
        f"ASSET={payload['asset']} | "
        f"POINT={payload['point']} | "
        f"TYPE=BEARING_OUTER | "
        f"TS={payload['timestamp']}"
    )


if __name__ == "__main__":
    while True:
        send_signal()
        time.sleep(1)

