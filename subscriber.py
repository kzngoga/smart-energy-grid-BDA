import json
import os
import psycopg2
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from utils import get_db_connection

# Load env variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# MQTT configuration
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT   = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC  = "energy/meters/#"

# Save reading to database
def save_reading(conn, data):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO energy_readings
                    (meter_id, timestamp, power, voltage, current, frequency, energy)
                VALUES
                    (%(meter_id)s, %(timestamp)s, %(power)s, %(voltage)s,
                     %(current)s, %(frequency)s, %(energy)s)
            """, data)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

# Called when subscriber connects to EMQX broker
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to EMQX broker")
        client.subscribe(MQTT_TOPIC)
        print(f"Listening on topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect - Code: {reason_code}")

# Called every time a meter publishes a reading
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        save_reading(userdata["conn"], data)
        print(f"Saved reading from meter {data['meter_id']} at {data['timestamp']}")

    except Exception as e:
        print(f"Error processing message: {e}")

# Main App Function
def main():
    conn = get_db_connection()
    print("Connected to TimescaleDB successfully!")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata={"conn": conn})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT)
    print("Subscriber is running...")
    client.loop_forever()


if __name__ == "__main__":
    main()
