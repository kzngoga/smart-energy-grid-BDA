-- Smart Energy Grid: Baseline Queries
-- Run these with \timing enabled in psql to capture execution times
-- Enable timing: \timing

-- Q1: Hourly average power consumption today
SELECT
    time_bucket('1 hour', timestamp) AS hour,
    AVG(power)                       AS avg_power_kw
FROM energy_readings
WHERE timestamp >= DATE_TRUNC('day', NOW())
  AND timestamp <  DATE_TRUNC('day', NOW()) + INTERVAL '1 day'
GROUP BY hour
ORDER BY hour;

-- Q2: Peak 15-minute periods in the past 7 days
SELECT
    time_bucket('15 minutes', timestamp) AS bucket,
    AVG(power)                           AS avg_power_kw
FROM energy_readings
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY bucket
ORDER BY avg_power_kw DESC
LIMIT 10;

-- Q3: Monthly total energy consumption per meter
SELECT
    meter_id,
    DATE_TRUNC('month', timestamp) AS month,
    SUM(energy)                    AS total_energy_kwh
FROM energy_readings
GROUP BY meter_id, month
ORDER BY meter_id, month;

-- Q4: Full dataset aggregate (count, avg, max, min power)
SELECT
    COUNT(*)   AS total_readings,
    AVG(power) AS avg_power_kw,
    MAX(power) AS max_power_kw,
    MIN(power) AS min_power_kw
FROM energy_readings;
