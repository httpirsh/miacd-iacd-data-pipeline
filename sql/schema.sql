-- PostgreSQL Schema for CO2 Emissions Data Pipeline

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS yearly_summary CASCADE;
DROP TABLE IF EXISTS country_summary CASCADE;
DROP TABLE IF EXISTS raw_emissions CASCADE;

-- 1. Raw Emissions Table (7 columns matching reduced_co2.csv)
CREATE TABLE raw_emissions (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    iso_code VARCHAR(10),
    population BIGINT,
    gdp DOUBLE PRECISION,
    co2 DOUBLE PRECISION,
    co2_per_capita DOUBLE PRECISION,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(country, year)
);

-- Create indexes for common queries
CREATE INDEX idx_raw_country ON raw_emissions(country);
CREATE INDEX idx_raw_year ON raw_emissions(year);
CREATE INDEX idx_raw_iso_code ON raw_emissions(iso_code);
CREATE INDEX idx_raw_country_year ON raw_emissions(country, year);

-- 2. Country Summary Table (aggregated by country)
CREATE TABLE country_summary (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) UNIQUE NOT NULL,
    iso_code VARCHAR(10),
    
    -- Total Emissions
    total_co2 DOUBLE PRECISION,
    avg_co2_per_capita DOUBLE PRECISION,
    
    -- Latest Data (most recent year)
    latest_year INTEGER,
    latest_population BIGINT,
    latest_co2 DOUBLE PRECISION,
    latest_co2_per_capita DOUBLE PRECISION,
    
    -- Historical
    first_year INTEGER,
    years_with_data INTEGER,
    
    -- Growth
    co2_growth_rate DOUBLE PRECISION,
    
    -- Rankings
    global_rank INTEGER,
    per_capita_rank INTEGER,
    
    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_country_name ON country_summary(country);
CREATE INDEX idx_country_rank ON country_summary(global_rank);

-- 3. Yearly Summary Table (aggregated by year)
CREATE TABLE yearly_summary (
    id SERIAL PRIMARY KEY,
    year INTEGER UNIQUE NOT NULL,
    
    -- Global Totals
    total_global_co2 DOUBLE PRECISION,
    total_global_population BIGINT,
    avg_co2_per_capita DOUBLE PRECISION,
    
    -- Stats
    num_countries INTEGER,
    max_country_co2 DOUBLE PRECISION,
    max_country_name VARCHAR(100),
    
    -- Growth
    yoy_growth_rate DOUBLE PRECISION,
    
    -- Metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_yearly_year ON yearly_summary(year);

-- Create views for common queries

-- View: Top 10 Polluters (Total CO2)
CREATE OR REPLACE VIEW top_polluters AS
SELECT 
    country,
    iso_code,
    total_co2,
    latest_co2,
    latest_year,
    global_rank
FROM country_summary
WHERE total_co2 IS NOT NULL
ORDER BY total_co2 DESC
LIMIT 10;

-- View: Top 10 Per Capita Polluters
CREATE OR REPLACE VIEW top_per_capita AS
SELECT 
    country,
    iso_code,
    avg_co2_per_capita,
    latest_co2_per_capita,
    latest_year,
    per_capita_rank
FROM country_summary
WHERE avg_co2_per_capita IS NOT NULL
ORDER BY avg_co2_per_capita DESC
LIMIT 10;

-- View: Recent Trends (Last 20 years)
CREATE OR REPLACE VIEW recent_trends AS
SELECT 
    year,
    total_global_co2,
    avg_co2_per_capita,
    yoy_growth_rate,
    num_countries
FROM yearly_summary
WHERE year >= (SELECT MAX(year) - 20 FROM yearly_summary)
ORDER BY year DESC;



-- Comments for documentation
COMMENT ON TABLE raw_emissions IS 'Raw CO2 emissions data from Kafka stream';
COMMENT ON TABLE country_summary IS 'Aggregated statistics by country';
COMMENT ON TABLE yearly_summary IS 'Aggregated statistics by year';
COMMENT ON VIEW top_polluters IS 'Top 10 countries by total CO2 emissions';
COMMENT ON VIEW top_per_capita IS 'Top 10 countries by per capita CO2 emissions';
