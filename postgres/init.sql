-- database: co2_data (matching your original setup)
-- user: postgres / postgres

-- table to store the clustering results
CREATE TABLE IF NOT EXISTS co2_clusters (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER,
    country VARCHAR(100),
    iso_code VARCHAR(10),
    avg_co2 DECIMAL(15,4),
    avg_co2_per_capita DECIMAL(15,4),
    avg_gdp DECIMAL(20,4),
    avg_population DECIMAL(20,4),
    cluster INTEGER,
    processing_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- table to store cluster statistics
CREATE TABLE IF NOT EXISTS cluster_stats (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER,
    cluster INTEGER,
    num_countries INTEGER,
    avg_co2_cluster DECIMAL(15,4),
    avg_co2_per_capita_cluster DECIMAL(15,4),
    avg_gdp_cluster DECIMAL(20,4),
    processing_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- indexes for better performance
CREATE INDEX IF NOT EXISTS idx_co2_clusters_country ON co2_clusters(country);
CREATE INDEX IF NOT EXISTS idx_co2_clusters_cluster ON co2_clusters(cluster);
CREATE INDEX IF NOT EXISTS idx_co2_clusters_batch ON co2_clusters(batch_id);

-- view for cluster analysis
CREATE OR REPLACE VIEW cluster_analysis AS
SELECT 
    cluster,
    COUNT(*) as country_count,
    ROUND(AVG(avg_co2), 2) as avg_co2,
    ROUND(AVG(avg_co2_per_capita), 2) as avg_co2_per_capita,
    ROUND(AVG(avg_gdp), 2) as avg_gdp
FROM co2_clusters
GROUP BY cluster
ORDER BY cluster;