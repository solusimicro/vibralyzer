import json
import os
import sys
import numpy as np
import yaml
import paho.mqtt.client as mqtt
from core.feature_pipeline import FeaturePipeline

# =========================
# LOAD MACHINE CONFIG
# =========================
yaml_path = os.path.join("config", "machine.yaml")

if not os.path.exists(yaml_path):
    print(f"❌ File {yaml_path} tidak ditemukan!")
    sys.exit(1)

with open(yaml_path, "r") as f:
    MACHINE_CONFIG_RAW = yaml.safe_load(f)

# normalize asset keys: strip + uppercase
MACHINE_CONFIG = {k.strip().upper(): v for k, v in MACHINE_CONFIG_RAW.items()}

print("✅ Loaded machine assets:", list(MACHINE_CONFIG.keys()))

# =========================
# INIT PIPELINE
# =========================
pipeline = FeaturePipeline()
FS = 25600

# =========================
# MQTT CALLBACKS
# =========================
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT connected")
    client.subscribe("vibration/raw/#")
    print("📡 Subscribed to: vibration/raw/#")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        # -------------------------
        # ASSET
        # -------------------------
        raw_asset = payload.get("asset")
        asset = ''.join(c for c in str(raw_asset) if c.isprintable()).strip().upper()
        if not asset or asset == "NONE":
            return

        # -------------------------
        # POINT
        # -------------------------
        raw_point = payload.get("point", "UNKNOWN")
        point = ''.join(c for c in str(raw_point) if c.isprintable()).strip().upper()

        if asset not in MACHINE_CONFIG:
            print(f"⚠️ Asset '{asset}' tidak ditemukan di machine.yaml")
            return

        # -------------------------
        # SIGNAL
        # -------------------------
        signal = payload.get("acceleration_g", payload.get("signal", []))
        signal = np.asarray(signal, dtype=float)

        if len(signal) < 28:
            print(f"⚠️ Signal terlalu pendek ({len(signal)}) untuk {asset}")
            return

        # -------------------------
        # TEMPERATURE (SAFE)
        # -------------------------
        temperature = None
        temp_raw = payload.get("temperature_c", payload.get("temperature"))
        if temp_raw is not None:
            try:
                temperature = float(temp_raw)
            except ValueError:
                print(f"⚠️ Invalid temperature value: {temp_raw}")

        # -------------------------
        # CONFIG
        # -------------------------
        machine = MACHINE_CONFIG[asset]
        rpm = machine.get("rpm", 0)

        # -------------------------
        # PROCESS
        # -------------------------
        pipeline.process(
            signal=signal,
            fs=FS,
            asset=asset,
            point=point,
            rpm=rpm,
            temperature=temperature
        )

    except Exception as e:
        print("❌ Error processing message:", e)

# =========================
# MQTT CLIENT
# =========================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()


