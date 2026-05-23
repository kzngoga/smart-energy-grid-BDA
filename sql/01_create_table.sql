-- Smart Energy Grid: Table Creation
-- Creates the main energy_readings table to store IoT meter data

CREATE TABLE IF NOT EXISTS energy_readings (
    meter_id    VARCHAR(20)     NOT NULL,
    timestamp   TIMESTAMPTZ     NOT NULL,
    power       DOUBLE PRECISION NOT NULL,   -- kW
    voltage     DOUBLE PRECISION NOT NULL,   -- V
    current     DOUBLE PRECISION NOT NULL,   -- A
    frequency   DOUBLE PRECISION NOT NULL,   -- Hz
    energy      DOUBLE PRECISION NOT NULL    -- kWh
);
