-- Smart Energy Grid: Chunk Interval Experimentation
-- Creates two additional hypertables with different chunk intervals for comparison

-- 3-hour chunk hypertable
CREATE TABLE IF NOT EXISTS energy_readings_3h (
    meter_id    VARCHAR(20)      NOT NULL,
    timestamp   TIMESTAMPTZ      NOT NULL,
    power       DOUBLE PRECISION NOT NULL,
    voltage     DOUBLE PRECISION NOT NULL,
    current     DOUBLE PRECISION NOT NULL,
    frequency   DOUBLE PRECISION NOT NULL,
    energy      DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable(
    'energy_readings_3h',
    'timestamp',
    chunk_time_interval => INTERVAL '3 hours',
    if_not_exists => TRUE
);

-- 1-week chunk hypertable
CREATE TABLE IF NOT EXISTS energy_readings_week (
    meter_id    VARCHAR(20)      NOT NULL,
    timestamp   TIMESTAMPTZ      NOT NULL,
    power       DOUBLE PRECISION NOT NULL,
    voltage     DOUBLE PRECISION NOT NULL,
    current     DOUBLE PRECISION NOT NULL,
    frequency   DOUBLE PRECISION NOT NULL,
    energy      DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable(
    'energy_readings_week',
    'timestamp',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

-- Copy data from the main hypertable
INSERT INTO energy_readings_3h   SELECT * FROM energy_readings;
INSERT INTO energy_readings_week SELECT * FROM energy_readings;

-- Verify chunk distribution
SELECT hypertable_name, num_chunks
FROM timescaledb_information.hypertables
WHERE hypertable_name IN ('energy_readings', 'energy_readings_3h', 'energy_readings_week');

-- Inspect chunk ranges
SELECT chunk_name, range_start, range_end
FROM timescaledb_information.chunks
WHERE hypertable_name = 'energy_readings'
LIMIT 5;

SELECT chunk_name, range_start, range_end
FROM timescaledb_information.chunks
WHERE hypertable_name = 'energy_readings_3h'
LIMIT 5;

SELECT chunk_name, range_start, range_end
FROM timescaledb_information.chunks
WHERE hypertable_name = 'energy_readings_week'
LIMIT 5;
