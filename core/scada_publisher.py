import json
import paho.mqtt.publish as publish

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
    recommendation=None    # 👈 TAMBAHKAN (INI SAJA)
):
    payload = {
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

    # Optional fields (AMAN)
    if alarm_code is not None:
        payload["alarm_code"] = alarm_code

    if recommendation:
        payload["recommendation"] = recommendation   # 👈 1 BARIS PENTING

    topic = f"vibration/feature/{asset}/{point}"
    publish.single(topic, json.dumps(payload), hostname="localhost")

