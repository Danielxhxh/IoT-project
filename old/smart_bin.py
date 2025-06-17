import paho.mqtt.client as mqtt
import time
import random
import threading

BROKER = "localhost"
PORT = 1883
N_BINS = 5
MAX_CAPACITY = 100
PUBLISH_INTERVAL = 2  # in seconds

# Shared state between publishing and receiving commands
state = [0 for _ in range(N_BINS)]
m_max_list = [random.randint(2, 5) for _ in range(N_BINS)]

def on_message(client, userdata, msg):
    bin_index = userdata["index"]
    # if the topic of the message is smartbins/bin_id/collect (sent by the central station) then empty bin
    if msg.topic == f"smartbins/bin_{bin_index+1}/collect":
        print(f"[bin_{bin_index+1}] Ricevuto comando di svuotamento.")
        state[bin_index] = 0

def markovChainSimulation(bin_index,m_max):
    # Simulate a Markov chain process: random increment of itemans in a bin, this simulate a uniform distribution over 0,..,M^i_{max}
    k = random.randint(0, m_max)
    # From a generic state s_i = p (state[bin_index] = p) choose the next reachable state s'_i: minimum between current value state s_i + k (state[bin_index] + k) and MAX_CAPACITY 
    state[bin_index] = min(state[bin_index] + k, MAX_CAPACITY)
    return state

def simulate_bin(bin_index):
    bin_id = f"bin_{bin_index+1}"
    m_max = m_max_list[bin_index]

    client = mqtt.Client(client_id=bin_id, userdata={"index": bin_index})
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(f"smartbins/{bin_id}/collect")
    client.loop_start()

    while True:

        state = markovChainSimulation(bin_index,m_max)

        # Publish current level
        topic = f"smartbins/{bin_id}/fill_level"
        client.publish(topic, str(state[bin_index]))
        print(f"[{bin_id}] Livello pubblicato: {state[bin_index]}%")
        time.sleep(PUBLISH_INTERVAL)

if __name__ == "__main__":
    threads = []
    # Multithreading code, each bin execute indipendently the code
    for i in range(N_BINS):
        t = threading.Thread(target=simulate_bin, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
