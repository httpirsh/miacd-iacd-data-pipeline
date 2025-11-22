-- Database: co2_data
-- User: co2_user / co2_password
-- Schema for CO2 Emissions Data Pipeline

-- Main table: raw_emissions (7 columns matching CSV dataset)
CREATE TABLE IF NOT EXISTS raw_emissions (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    year INTEGER,
    iso_code VARCHAR(10),
    population DOUBLE PRECISION,
    gdp DOUBLE PRECISION,
    co2 DOUBLE PRECISION,
    co2_per_capita DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated table: country_summary
CREATE TABLE IF NOT EXISTS country_summary (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    iso_code VARCHAR(10),
    total_co2 DOUBLE PRECISION,
    avg_co2_per_capita DOUBLE PRECISION,
    latest_year INTEGER,
    latest_co2 DOUBLE PRECISION,
    data_points INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated table: yearly_summary
CREATE TABLE IF NOT EXISTS yearly_summary (
    id SERIAL PRIMARY KEY,
    year INTEGER,
    total_global_co2 DOUBLE PRECISION,
    avg_co2_per_capita DOUBLE PRECISION,
    country_count INTEGER,
    growth_rate DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_raw_emissions_country ON raw_emissions(country);
CREATE INDEX IF NOT EXISTS idx_raw_emissions_year ON raw_emissions(year);
CREATE INDEX IF NOT EXISTS idx_raw_emissions_iso_code ON raw_emissions(iso_code);
CREATE INDEX IF NOT EXISTS idx_country_summary_country ON country_summary(country);
CREATE INDEX IF NOT EXISTS idx_yearly_summary_year ON yearly_summary(year);

-- View: Top 10 polluters by total CO2
CREATE OR REPLACE VIEW top_polluters AS
SELECT 
    country,
    iso_code,
    total_co2,
    latest_co2,
    latest_year
FROM country_summary
ORDER BY total_co2 DESC
LIMIT 10;

-- View: Top 10 by per capita emissions
CREATE OR REPLACE VIEW top_per_capita AS
SELECT 
    country,
    iso_code,
    avg_co2_per_capita,
    latest_year
FROM country_summary
WHERE avg_co2_per_capita IS NOT NULL
ORDER BY avg_co2_per_capita DESC
LIMIT 10;

-- View: Recent trends (last 20 years)
CREATE OR REPLACE VIEW recent_trends AS
SELECT 
    year,
    total_global_co2,
    avg_co2_per_capita,
    country_count,
    growth_rate
FROM yearly_summary
WHERE year >= (SELECT MAX(year) - 20 FROM yearly_summary)
ORDER BY year DESC;
