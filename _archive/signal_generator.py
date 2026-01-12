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
    "PUMP_01": {"rpm": 1480, "point": "DE", "bpfo": 92,  "base_temp": 42.0},
    "PUMP_02": {"rpm": 2960, "point": "DE", "bpfo": 184, "base_temp": 45.0}
}

HF_RESONANCE = 8000  # Hz

# persistent temperature state
TEMP_STATE = {
    asset: info["base_temp"]
    for asset, info in MACHINES.items()
}

# ==========================
# Generate bearing fault signal
# ==========================
def generate_bearing_fault_signal(n=4096, fs=FS, rpm=0, bpfo=1):
    t = np.arange(n) / fs
    FR = rpm / 60

    base = 0.02 * np.sin(2 * np.pi * FR * t)
    hf_carrier = np.sin(2 * np.pi * HF_RESONANCE * t)

    impulse_interval = int(fs / bpfo) if bpfo > 0 else n
    impulses = np.zeros(n)
    impulses[::impulse_interval] = 1.0

    bearing_fault = 0.15 * impulses * hf_carrier
    noise = 0.003 * np.random.randn(n)

    return (base + bearing_fault + noise).tolist()

# ==========================
# Temperature model
# ==========================
def update_temperature(asset, fault_severity=1.0):
    """
    fault_severity:
        0.0 = normal
        1.0 = mild bearing fault
        >1.0 = severe fault
    """
    temp = TEMP_STATE[asset]

    # natural cooling / inertia
    temp += np.random.normal(0, 0.05)

    # fault heating
    temp += 0.15 * fault_severity

    # clamp to realistic range
    temp = max(25.0, min(temp, 110.0))

    TEMP_STATE[asset] = temp
    return round(temp, 2)

# ==========================
# Send signal via MQTT
# ==========================
def send_signals():
    for asset, info in MACHINES.items():
        signal_data = generate_bearing_fault_signal(
            n=4096,
            fs=FS,
            rpm=info["rpm"],
            bpfo=info["bpfo"]
        )

        # temperature increases with bearing fault
        temperature = update_temperature(asset, fault_severity=1.0)

        payload = {
            "schema_version": "1.1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "asset": asset,
            "point": info["point"],
            "fs": FS,
            "rpm": info["rpm"],
            "temperature_c": temperature,
            "acceleration_g": signal_data
        }

        topic = f"vibration/raw/{asset}/{info['point']}"

        publish.single(
            topic=topic,
            payload=json.dumps(payload),
            hostname=BROKER,
            qos=1
        )

        print(
            f"📡 PUBLISHED | {asset} | "
            f"Temp={temperature}°C | RPM={info['rpm']}"
        )

# ==========================
# Main loop
# ==========================
if __name__ == "__main__":
    while True:
        send_signals()
        time.sleep(1)


