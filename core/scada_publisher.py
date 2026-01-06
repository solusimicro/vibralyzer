import paho.mqtt.publish as publish

def publish_scada_features(asset, point, features, broker="localhost"):
    base_topic = f"vibration/feature/{asset}/{point}"

    for key, value in features.items():
        if value is None:
            continue

        publish.single(
            topic=f"{base_topic}/{key}",
            payload=str(value),
            hostname=broker,
            qos=1
        )


