import paho.mqtt.client as mqtt
import time
import random
import argparse
import json

MAX_INCREASE = 10

parser = argparse.ArgumentParser(description="Smart Bin MQTT Publisher")
parser.add_argument("--id", required=True, type=int, help="ID of the smart bin")
args = parser.parse_args()
bin_id = args.id

trash_level = 0

def on_connect(client, userdata, flags, rc):
    print(f"[Smart Bin {bin_id}] Connected with result code {rc}")
    client.subscribe(f"smartbin/commands/{bin_id}")

def on_message(client, userdata, msg):
    global trash_level
    try:
        command = json.loads(msg.payload.decode())
        if command.get("action") == "empty":
            print(f"[Smart Bin {bin_id}] Received empty command.")
            trash_level = 0
    except json.JSONDecodeError:
        print(f"[Smart Bin {bin_id}] Received invalid command.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_start()

try:
    while True:
        k = random.randint(0, MAX_INCREASE)
        trash_level = min(trash_level + k, 100)
        payload = {
            "id": bin_id,
            "trash": f"{trash_level}%"
        }

        client.publish("smartbin/trash", json.dumps(payload))
        print(f"[Smart Bin {bin_id}] Sent:", payload)
        time.sleep(2)

except KeyboardInterrupt:
    print(f"[Smart Bin {bin_id}] Stopped.")
finally:
    client.loop_stop()
    client.disconnect()
