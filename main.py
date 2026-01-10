# ============================================================
# MAIN – VIBRATION EDGE PROCESSOR
# ============================================================

import json

from core.mqtt_client import start_mqtt
from core.signal_buffer import SignalBuffer
from core.feature_pipeline import FeaturePipeline


# ============================================================
# INIT
# ============================================================
buffer = SignalBuffer(
    window_size=4096,
    overlap=0.5
)

pipeline = FeaturePipeline()


# ============================================================
# MQTT CALLBACK
# ============================================================
def on_message(msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))

        signal = data.get("signal", [])
        fs = data.get("fs", 1000)
        rpm = data.get("rpm")

        asset = data.get("asset", "UNKNOWN")
        point = data.get("point", "UNKNOWN")

        # Push to rolling buffer
        windows = buffer.push(signal)

        for win in windows:
            # =====================================
            # PIPELINE = PROCESS + PUBLISH
            # =====================================
            pipeline.process(
                signal=win,
                fs=fs,
                rpm=rpm,
                asset=asset,
                point=point
            )

    except Exception as e:
        print("❌ ERROR processing message:", e)


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    start_mqtt(
        broker="localhost",
        port=1883,
        topic="vibration/raw/#",
        on_message_callback=on_message,
        qos=1
    )
