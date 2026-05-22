import random
from datetime import datetime, timedelta, timezone
from utils import get_db_connection, get_power_by_hour, generate_meter_ids

# Config
NUM_METERS         = 1000
PUBLISH_INTERVAL   = 300
WEEKS_OF_DATA      = 4
PROGRESS_INTERVAL  = 100_000

# Generate one reading per meter for a given timestamp
def generate_batch(meter_ids, timestamp):
    batch = []
    for meter_id in meter_ids:
        power   = get_power_by_hour(timestamp.hour)
        voltage = round(random.uniform(218.0, 242.0), 2)
        batch.append((
            meter_id,
            timestamp,
            round(power, 3),
            voltage,
            round(power * 1000 / voltage, 3),
            round(random.uniform(49.8, 50.2), 2),
            round(power * (PUBLISH_INTERVAL / 3600), 4)
        ))
    return batch


# Main App Function
def load_historical_data():
    conn = get_db_connection()
    cur  = conn.cursor()

    meter_ids    = generate_meter_ids(NUM_METERS)
    start_time   = datetime.now(timezone.utc) - timedelta(weeks=WEEKS_OF_DATA)
    current_time = start_time
    end_time     = datetime.now(timezone.utc)
    total        = 0

    print(f"Loading {WEEKS_OF_DATA} weeks of data for {NUM_METERS} meters...")
    print(f"From {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}\n")

    while current_time <= end_time:
        # generate one reading per meter for this timestamp
        batch = generate_batch(meter_ids, current_time)

        # bulk insert the entire batch
        cur.executemany("""
            INSERT INTO energy_readings
                (meter_id, timestamp, power, voltage, current, frequency, energy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, batch)
        conn.commit()

        total        += len(batch)
        current_time += timedelta(minutes=5)

        if total % PROGRESS_INTERVAL == 0:
            print(f"Inserted {total:,} rows...")

    print(f"\nDone! Total rows inserted: {total:,}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    load_historical_data()