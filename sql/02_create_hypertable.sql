-- Smart Energy Grid: Hypertable Creation
-- Converts energy_readings into a TimescaleDB hypertable with a 1-day chunk interval

SELECT create_hypertable(
    'energy_readings',
    'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Verify hypertable creation
SELECT hypertable_name, num_chunks
FROM timescaledb_information.hypertables;
