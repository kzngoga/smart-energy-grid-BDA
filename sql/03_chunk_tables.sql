-- Smart Energy Grid: Chunk Interval Experimentation
-- Creates two additional hypertables with different chunk intervals
-- and loads identical data from energy_readings for performance comparison
 
-- Create tables with the same structure as energy_readings
CREATE TABLE energy_readings_3h   (LIKE energy_readings INCLUDING ALL);
CREATE TABLE energy_readings_week (LIKE energy_readings INCLUDING ALL);
 
-- Convert to hypertables with different chunk intervals
SELECT create_hypertable('energy_readings_3h',   'timestamp', chunk_time_interval => INTERVAL '3 hours');
SELECT create_hypertable('energy_readings_week', 'timestamp', chunk_time_interval => INTERVAL '1 week');
 
-- Load identical data from energy_readings
INSERT INTO energy_readings_3h   SELECT * FROM energy_readings;
INSERT INTO energy_readings_week SELECT * FROM energy_readings;