-- Smart Energy Grid: Compression
-- Enables TimescaleDB compression on all three hypertables and checks storage savings

-- Check disk usage BEFORE compression
SELECT
    hypertable_name,
    pg_size_pretty(hypertable_size(format('%I', hypertable_name)::regclass)) AS size_before
FROM timescaledb_information.hypertables
WHERE hypertable_name IN ('energy_readings', 'energy_readings_3h', 'energy_readings_week');

-- Enable compression on energy_readings (1-day chunks)
ALTER TABLE energy_readings
    SET (
        timescaledb.compress,
        timescaledb.compress_orderby = 'timestamp DESC'
    );

SELECT add_compression_policy('energy_readings', INTERVAL '24 hours');

-- Manually compress existing chunks for immediate effect
SELECT compress_chunk(c) FROM show_chunks('energy_readings') c;

-- Enable compression on energy_readings_3h
ALTER TABLE energy_readings_3h
    SET (
        timescaledb.compress,
        timescaledb.compress_orderby = 'timestamp DESC'
    );

SELECT add_compression_policy('energy_readings_3h', INTERVAL '24 hours');

SELECT compress_chunk(c) FROM show_chunks('energy_readings_3h') c;

-- Enable compression on energy_readings_week
ALTER TABLE energy_readings_week
    SET (
        timescaledb.compress,
        timescaledb.compress_orderby = 'timestamp DESC'
    );

SELECT add_compression_policy('energy_readings_week', INTERVAL '24 hours');

SELECT compress_chunk(c) FROM show_chunks('energy_readings_week') c;

-- Check disk usage AFTER compression
SELECT
    hypertable_name,
    pg_size_pretty(hypertable_size(format('%I', hypertable_name)::regclass)) AS size_after
FROM timescaledb_information.hypertables
WHERE hypertable_name IN ('energy_readings', 'energy_readings_3h', 'energy_readings_week');
