# core/mqtt_client.py
import paho.mqtt.client as mqtt

def start_mqtt(broker, port, topic, on_message_callback, qos=1):

    def _on_connect(client, userdata, flags, reason_code, properties=None):
        print("MQTT connected:", reason_code)
        client.subscribe(topic, qos=qos)
        print("Subscribed to:", topic)

    def _on_message(client, userdata, message):
        on_message_callback(message)

    client = mqtt.Client(
        client_id="vibralyzer",
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect = _on_connect
    client.on_message = _on_message

    client.connect(broker, port)
    client.loop_forever()


