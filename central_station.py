import paho.mqtt.client as mqtt
import yaml
import json
import threading
import time
import sys


# Load configuration from YAML
def load_config(filepath="conf.yaml"):
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)
        return data

# Config file reading
config = load_config()
COST_MATRIX = config["COST_MATRIX"]
CLEANING_INTERVAL = config.get("CLEANING_INTERVAL", 30)
UPDATING_FREQUENCY = config.get("UPDATING_FREQUENCY", 5)
TRASH_LEVEL_THRESHOLD = config.get("TRASH_LEVEL_THRESHOLD", 80)

bins_to_empty = set()
lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")

        # Subscribe to each bin's fill_level topic (excluding 0, the central station)
        num_bins = len(COST_MATRIX)
        for bin_id in range(1, num_bins):
            topic = f"smartbin/{bin_id}/fill_level"
            client.subscribe(topic)
            print(f"Subscribed to: {topic}")

        # Start periodic emptying thread
        threading.Thread(
            target=empty_bins_periodically,
            args=(client, CLEANING_INTERVAL, UPDATING_FREQUENCY),
            daemon=True
        ).start()
    else:
        print(f"Connection failed with code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        level_str = payload.get("trash")
        topic_parts = msg.topic.split("/")
        if len(topic_parts) >= 3 and topic_parts[0] == "smartbin":
            bin_id = int(topic_parts[1])

        if bin_id is None or level_str is None:
            print("⚠️ Malformed message:", payload)
            return

        level = int(level_str.strip('%'))

        if level > TRASH_LEVEL_THRESHOLD:
            with lock:
                bins_to_empty.add(bin_id)

    except Exception as e:
        print("❌ Error processing message:", e)



def find_min_route_and_empty(COST_MATRIX, bins_to_empty, client):
    if not bins_to_empty:
        return

    bins = list(bins_to_empty)
    visited = set()
    current = 0  # Start at central station (index 0)
    total_cost = 0
    route = [0]  # Start from central station

    while len(visited) < len(bins):
        min_cost = float('inf')
        next_bin = None

        for bin_id in bins:
            if bin_id in visited:
                continue
            cost = COST_MATRIX[current][bin_id]
            if cost != -1 and cost < min_cost:
                min_cost = cost
                next_bin = bin_id

        if next_bin is None:
            print("⚠️ Error: No reachable unvisited bins.")
            break

        total_cost += min_cost
        route.append(next_bin)
        visited.add(next_bin)
        current = next_bin

        # 👉 Send MQTT command to empty the bin
        topic = f"smartbin/commands/{next_bin}"
        payload = json.dumps({"action": "empty"})
        client.publish(topic, payload)

    # Return to central station
    back_cost = COST_MATRIX[current][0]
    if back_cost != -1:
        total_cost += back_cost
        route.append(0)
    else:
        print("⚠️ Error: Cannot return to central station.")

    print(f"🚚 Route taken: {route}")
    print(f"✅ Emptied bins: {visited}")
    print(f"💰 Total cleaning cost: {total_cost}\n")

    # Clear the bins after they've been emptied
    bins_to_empty.clear()

    if not bins_to_empty:
        return

    bins = list(bins_to_empty)
    visited = set()
    current = 0  # Start at central station (index 0)
    total_cost = 0
    route = [0]  # start from central station

    while len(visited) < len(bins):
        min_cost = float('inf')
        next_bin = None

        for bin_id in bins:
            if bin_id in visited:
                continue
            cost = COST_MATRIX[current][bin_id]
            if cost != -1 and cost < min_cost:
                min_cost = cost
                next_bin = bin_id

        if next_bin is None:
            print("⚠️ Error: No reachable unvisited bins.")
            break

        total_cost += min_cost
        route.append(next_bin)
        visited.add(next_bin)
        current = next_bin

    # Return to central station
    back_cost = COST_MATRIX[current][0]
    if back_cost != -1:
        total_cost += back_cost
        route.append(0)
    else:
        print("⚠️ Error: Cannot return to central station.")

    print(f"🚚 Route taken: {route}")
    print(f"🧹 Emptied bins: {visited}")
    print(f"💰 Total cleaning cost: {total_cost}")

    # After emptying, clear the set
    bins_to_empty.clear()


def empty_bins_periodically(client, CLEANING_INTERVAL, UPDATING_FREQUENCY):
    while True:
        
        for i in range(CLEANING_INTERVAL, 0, -1):
            print(f"\r⏳ Checking bins in: {i:2d}s", end='', flush=True)
            time.sleep(1)
        print()  # Move to the next line after countdown finishes

        

        with lock:
            if bins_to_empty:
                find_min_route_and_empty(COST_MATRIX, bins_to_empty, client)
            else: print("\nNo bins to empty.\n")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)
print("🚀 Central station starting...")



client.loop_forever()
