# core/scada_publisher.py
import json
import paho.mqtt.publish as publish
from collections.abc import Mapping

BROKER = "localhost"


def flatten_dict(d: dict, parent_key: str = "", sep: str = "_"):
    """
    Flatten nested dict or list into flat key-value pairs.
    Lists will be joined with commas.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, Mapping):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            # if list of dicts, flatten each dict with index
            if all(isinstance(i, Mapping) for i in v):
                for idx, item in enumerate(v):
                    items.update(flatten_dict(item, f"{new_key}{sep}{idx}", sep=sep))
            else:
                # list of values → join as string
                items[new_key] = ",".join(map(str, v))
        else:
            items[new_key] = v
    return items


def publish_scada_features(
    asset: str,
    point: str,
    rpm: float,
    features: dict,
    context: dict,
    alarm_code: int = None,
    recommendation: dict = None
):
    """
    Publish hasil analisis vibrasi ke SCADA (FLAT JSON).
    Semua nested dict/list akan di-flatten otomatis.
    """

    # =====================================================
    # 1️⃣ BASE PAYLOAD
    # =====================================================
    payload = {
        "asset": asset,
        "point": point,
        "rpm": rpm
    }

    if alarm_code is not None:
        payload["alarm_code"] = alarm_code

    # =====================================================
    # 2️⃣ FLATTEN FEATURES + CONTEXT
    # =====================================================
    payload.update(flatten_dict(features))
    payload.update(flatten_dict(context))

    # =====================================================
    # 3️⃣ PUBLISH FEATURE TOPIC
    # =====================================================
    topic = f"vibration/feature/{asset}/{point}"
    publish.single(topic, json.dumps(payload), hostname=BROKER)

    # =====================================================
    # 4️⃣ PUBLISH RECOMMENDATION (SEPARATE TOPIC)
    # =====================================================
    if recommendation:
        rec_payload = flatten_dict(recommendation)
        rec_topic = f"vibration/recommendation/{asset}/{point}"
        publish.single(rec_topic, json.dumps(rec_payload), hostname=BROKER)

