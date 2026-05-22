import json
import os
import random
import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import sys
from utils import get_power_by_hour, generate_meter_ids

# Load environment variables
load_dotenv()
 
# MQTT broker config
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT   = int(os.getenv("MQTT_PORT"))
 
# Simulation config
NUM_METERS      = 1000   # number of smart meters to simulate
PUBLISH_INTERVAL = 300   # 5 minutes (300 seconds)

# Generate a meter reading
def generate_reading(meter_id):
    hour  = datetime.now().hour
    power = get_power_by_hour(hour)
    voltage = round(random.uniform(218.0, 242.0), 2)

    return {
        "meter_id":  meter_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "power":     round(power, 3),                        # kW
        "voltage":   voltage, # V (normal range)
        "current":   round(power / voltage * 1000, 3),           # A (I = P/V)
        "frequency": round(random.uniform(49.8, 50.2), 2),   # Hz
        "energy":    round(power * (PUBLISH_INTERVAL / 3600), 4)  # kWh
    }

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to EMQX broker")
    else:
        print(f"Connection failed with code {reason_code}")

# Publish one reading for each meter
def publish_readings(client, meter_ids):
    for meter_id in meter_ids:
        reading = generate_reading(meter_id)
        topic   = f"energy/meters/{meter_id}"
        payload = json.dumps(reading)
 
        client.publish(topic, payload)
 
    print(f"Published {len(meter_ids)} readings at {datetime.now().strftime('%H:%M:%S')}")

# Main App Function
def main():
    # Check for test mode (simulate every 10 seconds to test for 1 hour)
    test_mode = "--test" in sys.argv
    interval  = 10 if test_mode else PUBLISH_INTERVAL

    if test_mode:
        print("Test mode: publishing every 10 seconds")

    # Generate 1000 unique meter IDs
    meter_ids = generate_meter_ids(NUM_METERS)
    print(f"Simulating {NUM_METERS} meters")
 
    # Set up MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()  # runs MQTT in background thread
 
    print(f"Publishing every {interval // 60} minutes...\n")
 
    try:
        while True:
            publish_readings(client, meter_ids)
            time.sleep(interval)  # wait 5 minutes before next round
 
    except KeyboardInterrupt: # Stop simulator using Ctrl+C
        print("\nSimulator stopped")
        client.loop_stop()
        client.disconnect()

# Main App Function
if __name__ == "__main__":
    main()