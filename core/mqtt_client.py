# ============================================================
# core/mqtt_client.py
# MQTT Infra Layer (Subscribe & Publish)
# ============================================================

import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


# ============================================================
# MQTT SUBSCRIBER
# ============================================================
def start_mqtt(broker, port, topic, on_message_callback, qos=1):
    """
    MQTT client untuk menerima data getaran.
    Modul ini hanya menangani koneksi & subscription (infra layer).
    """

    # -------------------------------
    # CALLBACKS (API VERSION 2)
    # -------------------------------
    def _on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print("✅ MQTT connected")
            client.subscribe(topic, qos=qos)
            print(f"📡 Subscribed to: {topic}")
        else:
            print(f"❌ MQTT connection failed, code={reason_code}")

    def _on_message(client, userdata, message):
        try:
            on_message_callback(message)
        except Exception as e:
            print("❌ Error in message callback:", e)

    def _on_disconnect(client, userdata, reason_code, properties=None):
        print(f"⚠️ MQTT disconnected, code={reason_code}")

    # -------------------------------
    # CLIENT INIT
    # -------------------------------
    client = mqtt.Client(
        client_id="vibralyzer",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        clean_session=True
    )

    client.on_connect = _on_connect
    client.on_message = _on_message
    client.on_disconnect = _on_disconnect

    # -------------------------------
    # RELIABILITY
    # -------------------------------
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    # -------------------------------
    # CONNECT & LOOP
    # -------------------------------
    client.connect(broker, port, keepalive=60)
    client.loop_forever()


# ============================================================
# MQTT PUBLISHER (GENERIC)
# ============================================================
def mqtt_publish(topic: str, payload: dict, broker="localhost"):
    """
    Generic MQTT publish helper.
    Dipakai oleh SCADA publisher / recommendation / event.
    """
    publish.single(
        topic,
        json.dumps(payload),
        hostname=broker
    )

