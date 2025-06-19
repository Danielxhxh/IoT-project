# 🗑️ Smart Bin MQTT System

A simple IoT simulation using MQTT where smart trash bins periodically send their fill levels to a central station. The central station monitors these levels and issues commands to empty bins when needed, optimizing the route based on a cost matrix.

## 🚧 Setup

We highly recommend creating and activating a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

Then install all the necessary dependencies:
```bash
pip install -r requirements.txt
```

Make sure Mosquitto is installed and running.
On macOS, you can install and run it using:
```bash
brew install mosquitto
brew services start mosquitto  # Optional: runs Mosquitto in the background
```
or temporary foreground run (without brew services
```bash
mosquitto -v
```
## 🚀 Deployment

Before running the code, you can configure global settings in the `conf.yaml` file.  

There are two ways to deploy this project: an **automatic mode** (available only on macOS), or **manual mode**.

### 🤖 Automatic (macOS Only)

The script `launcher.py` will open five new terminal windows:  
- One for the **central station**  
- Four for each **smart bin**

To launch everything automatically, simply run:

```bash
python launcher.py

```
⚠️ Make sure your system allows terminal scripts to spawn new windows (this may require accessibility permissions in macOS).

### 💪 Manual
For manual deployment, open five terminal windows.

- In the first window, run the central station:
```bash
  python central_station.py
```

- In the remaining four terminals, run the smart bins by specifying their unique IDs:
```bash
  python smart_bin.py --id {id_number}
```
Replace {id_number} with a number between 0 and 4 (inclusive). Each bin must have a unique ID.


## 👨‍💻 Authors

- [@Danielxhxh](https://github.com/Danielxhxh)
- [@im-sofaking](https://github.com/im-sofaking)
- [@Prestijhonny](https://github.com/Prestijhonny)


