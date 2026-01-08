import json
import paho.mqtt.publish as publish

BROKER = "localhost"

def publish_scada_features(
    asset,
    point,
    rpm,
    health,
    vel_rms,
    iso_zone,
    iso_zone_code,
    faults,
    status,
    alarm_code=None,
    recommendation=None
):
    # ===============================
    # 1️⃣ FEATURE TOPIC
    # ===============================
    feature_payload = {
        "asset": asset,
        "point": point,
        "rpm": rpm,
        "health_index": health,
        "vel_rms": vel_rms,
        "iso_zone": iso_zone,
        "iso_zone_code": iso_zone_code,
        "status": status,
        "faults": faults
    }

    if alarm_code is not None:
        feature_payload["alarm_code"] = alarm_code

    feature_topic = f"vibration/feature/{asset}/{point}"

    publish.single(
        feature_topic,
        json.dumps(feature_payload),
        hostname=BROKER
    )

    # ===============================
    # 2️⃣ RECOMMENDATION TOPIC
    # ===============================
    if recommendation:
        rec_payload = {
            "priority": recommendation.get("priority"),
            "maintenance_type": recommendation.get("maintenance_type"),
            "recommended_in_days": recommendation.get("recommended_in_days"),
            "action": recommendation.get("action"),
            "notes": recommendation.get("notes")
        }

        rec_topic = f"vibration/recommendation/{asset}/{point}"

        publish.single(
            rec_topic,
            json.dumps(rec_payload),
            hostname=BROKER
        )
