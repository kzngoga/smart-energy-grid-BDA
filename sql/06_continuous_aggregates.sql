-- Smart Energy Grid: Continuous Aggregations
-- Creates 15-minute, hourly, and daily materialized views with automatic refresh policies

-- 15-minute aggregation view
CREATE MATERIALIZED VIEW energy_readings_15min
WITH (timescaledb.continuous) AS
SELECT
    meter_id,
    time_bucket('15 minutes', timestamp) AS bucket,
    AVG(power)   AS avg_power,
    MAX(power)   AS max_power,
    SUM(energy)  AS total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

SELECT add_continuous_aggregate_policy('energy_readings_15min',
    start_offset      => INTERVAL '3 days',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes');

-- Hourly aggregation view
CREATE MATERIALIZED VIEW energy_readings_1h
WITH (timescaledb.continuous) AS
SELECT
    meter_id,
    time_bucket('1 hour', timestamp) AS bucket,
    AVG(power)   AS avg_power,
    MAX(power)   AS max_power,
    SUM(energy)  AS total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

SELECT add_continuous_aggregate_policy('energy_readings_1h',
    start_offset      => INTERVAL '3 days',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Daily aggregation view
CREATE MATERIALIZED VIEW energy_readings_1d
WITH (timescaledb.continuous) AS
SELECT
    meter_id,
    time_bucket('1 day', timestamp) AS bucket,
    AVG(power)   AS avg_power,
    MAX(power)   AS max_power,
    SUM(energy)  AS total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

SELECT add_continuous_aggregate_policy('energy_readings_1d',
    start_offset      => INTERVAL '3 days',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 day');

-- Performance comparison: raw vs aggregated

-- Raw query (scans all rows)
SELECT
    time_bucket('15 minutes', timestamp) AS bucket,
    AVG(power) AS avg_power
FROM energy_readings
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY bucket
ORDER BY bucket;

-- Aggregated query (reads pre-computed view)
SELECT bucket, avg_power
FROM energy_readings_15min
WHERE bucket >= NOW() - INTERVAL '7 days'
ORDER BY bucket;
