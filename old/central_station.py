import paho.mqtt.client as mqtt
import time
import random

BROKER = "localhost"
PORT = 1883
N_BINS = 5
THRESHOLD = 20
CHECK_INTERVAL = 3  # in seconds

# Global state: actual levels of bins
fill_levels = {f"bin_{i+1}": 0 for i in range(N_BINS)}

# Cost matrix NxN filled with random value (from 1 up to 20)
cost_matrix = [[0 for _ in range(N_BINS)] for _ in range(N_BINS)]
for i in range(N_BINS):
    for j in range(i + 1, N_BINS):
        cost = random.randint(1, 20)
        cost_matrix[i][j] = cost
        cost_matrix[j][i] = cost

def on_connect(client, userdata, flags, rc):
    print("[Central] Connected to MQTT Broker (Mosquitto).")
    client.subscribe("smartbins/+/fill_level")

def on_message(client, userdata, msg):
    bin_id = msg.topic.split("/")[1]  # "bin_X"
    fill = int(msg.payload.decode())
    fill_levels[bin_id] = fill
    #print(f"[Central] Ricevuto {bin_id}: {fill}%")

def tsp_greedy(nodes, matrix):
    if not nodes:
        return [], 0

    start = nodes[0]
    visited = [start]
    unvisited = set(nodes[1:])
    total_cost = 0
    current = start

    while unvisited:
        next_node = min(unvisited, key=lambda x: matrix[current][x])
        total_cost += matrix[current][next_node]
        visited.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    # ritorno al nodo iniziale
    total_cost += matrix[current][start]
    visited.append(start)

    return visited, total_cost

def decision_loop(client):
    while True:

        # Select containers that are at least a certain full threshold
        selected_bins = [i for i in range(N_BINS) if fill_levels[f"bin_{i+1}"] >= THRESHOLD]

        if not selected_bins:
            print("[Central] No bin selected.\n")
            continue

        # Calculate TSP greedy algorithm 
        path, cost = tsp_greedy(selected_bins, cost_matrix)

        print(f"[Central] Bin to collect: {[f'bin_{i+1}' for i in selected_bins]}")
        print(f"[Central] Path (TSP greedy): {[f'bin_{i+1}' for i in path]}")
        print(f"[Central] Total cost: {cost}\n")

        # Send commands in order to empty bins
        for i in selected_bins:
            topic = f"smartbins/bin_{i+1}/collect"
            client.publish(topic, "collect")
            fill_levels[f"bin_{i+1}"] = 0

        # Wait before checks bins
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    # Initialization of data
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"central_station")
    client.on_connect = on_connect
    client.on_message = on_message
    # Broker Connection
    client.connect(BROKER, PORT)

    decision_loop(client)