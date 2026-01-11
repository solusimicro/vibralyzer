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

        # ambil asset
        raw_asset = payload.get("asset", None)
        asset = ''.join(c for c in str(raw_asset) if c.isprintable()).strip().upper()

        # skip payload kosong, NONE, atau invalid
        if not asset or asset == "NONE":
            return  # langsung abaikan tanpa warning

        # ambil point
        raw_point = payload.get("point", "UNKNOWN")
        point = ''.join(c for c in str(raw_point) if c.isprintable()).strip().upper()

        # debug optional
        # print("DEBUG: payload asset =", repr(raw_asset), "| normalized =", asset)

        if asset not in MACHINE_CONFIG:
            print(f"⚠️ Asset '{asset}' tidak ditemukan di machine.yaml, skip processing")
            return

        # ambil signal
        signal = np.array(payload.get("acceleration_g") or payload.get("signal") or [])

        if len(signal) < 28:
            print(f"⚠️ Signal terlalu pendek ({len(signal)} sampel) untuk asset {asset}, skip processing")
            return

        # ambil RPM & bearing
        machine = MACHINE_CONFIG[asset]
        rpm = machine.get("rpm", 0)
        bearing_data = machine.get("bearing", {})

        # proses pipeline
        pipeline.process(signal=signal, fs=FS, asset=asset, point=point, rpm=rpm)

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


