from core.mqtt_client import start_mqtt
from core.signal_buffer import SignalBuffer
from core.feature_pipeline import FeaturePipeline
from core.scada_publisher import publish_scada_features
import json

buffer = SignalBuffer(
    window_size=4096,
    overlap=0.5
)

pipeline = FeaturePipeline()

def on_message(msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))

        signal = data["signal"]
        fs = data["fs"]
        asset = data["asset"]
        point = data["point"]
        rpm = data.get("rpm")   # ✅ AMAN: boleh None

        windows = buffer.push(signal)

        for win in windows:
            features = pipeline.process(
                signal=win,
                fs=fs,
                asset=asset,
                point=point,
                rpm=rpm             # ⭐ INI KUNCI
            )

            publish_scada_features(asset, point, features)

            print(
                f"SCADA OUT [{asset}-{point}] "
                f"RPM={rpm} | "
                f"Health={features.get('health_index'):.3f}"
            )

    except Exception as e:
        print("❌ ERROR processing message:", e)

if __name__ == "__main__":
    start_mqtt(
        broker="localhost",
        port=1883,
        topic="vibration/raw/#",
        on_message_callback=on_message,
        qos=1
    )



