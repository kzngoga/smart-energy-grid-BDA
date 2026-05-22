# Smart Energy Grid

Simulates smart meter readings over MQTT (EMQX), stores them in TimescaleDB, and visualizes consumption with a Streamlit dashboard.

## Prerequisites

- Python 3.12+
- [EMQX](https://www.emqx.io/) MQTT broker
- PostgreSQL with [TimescaleDB](https://www.timescale.com/) and an `energy_readings` hypertable

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install paho-mqtt python-dotenv psycopg2-binary sqlalchemy pandas streamlit plotly
```

Create a `.env` file in the project root:

```env
MQTT_BROKER=localhost
MQTT_PORT=1883
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_grid
DB_USER=postgres
DB_PASSWORD=your_password
```

## Usage

Run each component in a separate terminal (subscriber and simulator need the broker; dashboard needs the database).

**Before starting the simulator**, run `subscriber.py` in another terminal so published readings are saved to TimescaleDB. Without it, messages are sent to MQTT but nothing is persisted.

| Script | Purpose |
|--------|---------|
| `python load_historical.py` | Seed ~4 weeks of historical readings (optional) |
| `python subscriber.py` | Subscribe to MQTT and insert readings into TimescaleDB (start before simulator) |
| `python simulator.py` | Publish live meter readings every 5 minutes (requires `subscriber.py` running) |
| `python simulator.py --test` | Same, but every 10 seconds for testing (requires `subscriber.py` running) |
| `streamlit run dashboard.py` | Analytics dashboard |

## Project layout

- `simulator.py` — MQTT publisher for 1000 simulated meters
- `subscriber.py` — MQTT consumer that writes to `energy_readings`
- `load_historical.py` — Bulk backfill for development
- `dashboard.py` — Streamlit + Plotly charts
- `utils.py` — DB helpers and meter simulation utilities
