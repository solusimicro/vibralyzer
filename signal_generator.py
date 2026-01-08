import json
import time
import numpy as np
import paho.mqtt.publish as publish

BROKER = "localhost"
TOPIC = "vibration/raw/PUMP_01/DE"
FS = 25600
RPM = 2880
FR = RPM / 60

def generate_signal(n=4096, fs=FS):
    t = np.arange(n) / fs
    signal = 0.02 * np.sin(2 * np.pi * FR * t)
    noise = 0.001 * np.random.randn(n)

    data = signal + noise
    mean_signal = round(float(np.mean(data)), 8)   # 👈 SATU NILAI

    return data.tolist(), mean_signal

def send_signal():
    signal_data, mean_signal = generate_signal()

    payload = {
        "asset": "PUMP_01",
        "point": "DE",
        "fs": FS,
        "rpm": RPM,
        "ts": time.time(),
        "signal": signal_data,
        "mean_signal": mean_signal    # 👈 TAMBAHAN
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
        f"MEAN={mean_signal:.6f} | "
        f"TS={payload['ts']:.3f}"
    )

if __name__ == "__main__":
    while True:
        send_signal()
        time.sleep(1)


