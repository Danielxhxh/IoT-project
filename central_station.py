import paho.mqtt.client as mqtt
import yaml
import json
import threading
import time

# Load the cost matrix from YAML
def load_cost_matrix(filepath="conf.yaml"):
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)
        return data["cost_matrix"]

cost_matrix = load_cost_matrix()

bins_to_empty = set()
lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("smartbin/trash")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        bin_id = payload.get("id")
        level_str = payload.get("trash")

        if bin_id is None or level_str is None:
            print("Malformed message:", payload)
            return

        level = int(level_str.strip('%'))
        # print(f"🗑️ Bin {bin_id} reports fill level: {level}%")

        if level > 80:
            # Add bin_id to bins_to_empty safely
            with lock:
                bins_to_empty.add(bin_id)

    except Exception as e:
        print("Error processing message:", e)


def find_min_route_and_empty(cost_matrix, bins_to_empty, client):
    updated_cost_matrix = [
        [value for j, value in enumerate(row) if j in bins_to_empty]
        for i, row in enumerate(cost_matrix) if i in bins_to_empty
    ]
    print("🗺️ Updated cost matrix for emptying bins:", updated_cost_matrix)


def empty_bins_periodically(client, interval=10):
    while True:
        time.sleep(interval)
        with lock:
            if bins_to_empty:
                find_min_route_and_empty(cost_matrix, bins_to_empty, client)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)
print("🚀 Central station starting...")

# Start periodic emptying thread
threading.Thread(target=empty_bins_periodically, args=(client,), daemon=True).start()

client.loop_forever()
