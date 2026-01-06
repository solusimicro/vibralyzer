import json
import time
import numpy as np
import paho.mqtt.publish as publish

BROKER = "localhost"
TOPIC = "vibration/raw/PUMP_01/DE"
FS = 25600
RPM = 3000          # ✅ 3000 RPM = 50 Hz
FR = RPM / 60       # running frequency

def generate_signal(n=4096, fs=FS):
    t = np.arange(n) / fs
    signal = 0.02 * np.sin(2 * np.pi * FR * t)
    noise = 0.001 * np.random.randn(n)
    return (signal + noise).tolist()

def send_signal():
    payload = {
        "asset": "PUMP_01",
        "point": "DE",
        "fs": FS,
        "rpm": RPM,              # ⭐ PENTING
        "ts": time.time(),
        "signal": generate_signal()
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
        f"LEN={len(payload['signal'])} | "
        f"TS={payload['ts']:.3f}"
    )

if __name__ == "__main__":
    while True:
        send_signal()
        time.sleep(1)


