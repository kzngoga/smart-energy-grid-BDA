import os
import random
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ─── Load environment variables ───
load_dotenv()


def get_db_connection():
    """Connect to TimescaleDB and return connection."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def get_power_by_hour(hour):
    """Return realistic power usage based on time of day."""
    if 6 <= hour <= 9:
        return random.uniform(3.0, 6.0)    # morning peak
    elif 17 <= hour <= 21:
        return random.uniform(4.0, 8.0)    # evening peak
    elif 23 <= hour or hour <= 5:
        return random.uniform(0.2, 1.5)    # night low usage
    else:
        return random.uniform(1.5, 3.5)    # daytime moderate


def generate_meter_ids(n):
    """Generate n unique 10-digit meter IDs."""
    ids = set()
    while len(ids) < n:
        ids.add(str(random.randint(1000000000, 9999999999)))
    return list(ids)

def get_db_engine():
    """Return a SQLAlchemy engine for pandas compatibility."""
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )