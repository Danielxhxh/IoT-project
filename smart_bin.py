import paho.mqtt.client as mqtt
import time
import random
import argparse
import json
import yaml

# Load configuration from YAML
def load_config(filepath="conf.yaml"):
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)
        return data

# Config file reading
config = load_config()
MAX_INCREASE = config["MAX_INCREASE"]
 

parser = argparse.ArgumentParser(description="Smart Bin MQTT Publisher")
parser.add_argument("--id", required=True, type=int, help="ID of the smart bin")
args = parser.parse_args()
bin_id = args.id

trash_level = 0

def on_connect(client, userdata, flags, rc):
    client.subscribe(f"smartbin/commands/{bin_id}")

def on_message(client, userdata, msg):
    global trash_level
    try:
        command = json.loads(msg.payload.decode())
        if command.get("action") == "empty":
            print("\r" + " " * 80 + "\r", end='')  # clear line
            print(f"[🗑️  Bin {bin_id}] Received empty command.")
            trash_level = 0
    except json.JSONDecodeError:
        print(f"\r[Smart Bin {bin_id}] Received invalid command.")

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
            "trash": f"{trash_level}%"
        }

        client.publish(f"smartbin/{bin_id}/fill_level", json.dumps(payload))
        bar_length = 20  # Length of the bar
        filled_length = int(trash_level / 100 * bar_length)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r🗑️  Bin {bin_id:2d} |{bar}| {trash_level:3d}%", end='', flush=True)
        time.sleep(2)

except KeyboardInterrupt:
    print(f"\r[Smart Bin {bin_id}] Stopped.")
finally:
    client.loop_stop()
    client.disconnect()
