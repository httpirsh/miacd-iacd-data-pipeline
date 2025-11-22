-- Database: co2_data (matching your original setup)
-- User: co2_user / co2_password

-- Tabela para armazenar os resultados do clustering
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

-- Tabela para estatísticas dos clusters
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

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_co2_clusters_country ON co2_clusters(country);
CREATE INDEX IF NOT EXISTS idx_co2_clusters_cluster ON co2_clusters(cluster);
CREATE INDEX IF NOT EXISTS idx_co2_clusters_batch ON co2_clusters(batch_id);

-- View para análise dos clusters
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

-- Inserir dados de teste
-- INSERT INTO co2_clusters (batch_id, country, iso_code, avg_co2, avg_co2_per_capita, avg_gdp, avg_population, cluster)
-- VALUES 
-- (0, 'Test Country', 'TST', 100.5, 2.5, 50000.0, 40000000.0, 0)
-- ON CONFLICT DO NOTHING;