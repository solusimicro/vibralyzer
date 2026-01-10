import json
import paho.mqtt.publish as publish

BROKER = "localhost"


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
    Publish hasil analisis getaran ke SCADA / MQTT.
    File ini tidak melakukan perhitungan atau keputusan apapun.
    """

    # =====================================================
    # 1️⃣ FEATURE & STATUS TOPIC
    # =====================================================
    payload = {
        "asset": asset,
        "point": point,
        "rpm": rpm,
        "features": features,
        "health_index": context.get("health_score"),
        "alarm_status": context.get("alarm_status"),
        "faults": context.get("fault_candidates"),
    }

    if alarm_code is not None:
        payload["alarm_code"] = alarm_code

    topic = f"vibration/feature/{asset}/{point}"

    publish.single(
        topic,
        json.dumps(payload),
        hostname=BROKER
    )

    # =====================================================
    # 2️⃣ MAINTENANCE RECOMMENDATION TOPIC
    # =====================================================
    if recommendation:
        rec_topic = f"vibration/recommendation/{asset}/{point}"

        publish.single(
            rec_topic,
            json.dumps(recommendation),
            hostname=BROKER
        )
