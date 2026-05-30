import json
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from backend.tools.bigquery_tool import insert_readings

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "factory/line")


def on_connect(client, userdata, flags, rc):
    print(f"connected to MQTT broker (rc={rc}), subscribing to {TOPIC_PREFIX}/#")
    client.subscribe(f"{TOPIC_PREFIX}/#")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        insert_readings([payload])
        print(
            f"inserted: {payload['sensor_name']} "
            f"line {payload['line_number']} = {payload['value']} {payload['unit']}"
        )
    except Exception as e:
        print(f"error processing message: {e}")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"failed to connect to MQTT broker: {e}")
        return

    client.loop_forever()


if __name__ == "__main__":
    main()
