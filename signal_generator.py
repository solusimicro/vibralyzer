# signal_generator.py
import json
import time
import numpy as np
import paho.mqtt.publish as publish
from datetime import datetime, timezone

BROKER = "localhost"
TOPIC = "vibration/raw/PUMP_01/DE"

FS = 25600
RPM = 2880
FR = RPM / 60


def generate_signal(n=4096, fs=FS):
    t = np.arange(n) / fs

    # 1X running frequency (healthy)
    signal = 0.02 * np.sin(2 * np.pi * FR * t)

    # low noise
    noise = 0.001 * np.random.randn(n)

    data = signal + noise
    return data.tolist()


def send_signal():
    signal_data = generate_signal()

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
        f"PUBLISHED | "
        f"ASSET={payload['asset']} | "
        f"POINT={payload['point']} | "
        f"RPM={payload['rpm']} | "
        f"LEN={len(signal_data)} | "
        f"TS={payload['timestamp']}"
    )


if __name__ == "__main__":
    while True:
        send_signal()
        time.sleep(1)


