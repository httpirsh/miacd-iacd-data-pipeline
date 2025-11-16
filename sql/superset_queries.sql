-- ============================================
-- CO2 Data Analysis - Useful SQL Queries
-- For use in Superset SQL Lab
-- ============================================

-- ====================
-- 1. GLOBAL TRENDS
-- ====================

-- Get key milestone years
SELECT 
    year,
    total_global_co2,
    yoy_growth_rate,
    CASE 
        WHEN year = 1900 THEN 'Industrial Era Begin'
        WHEN year = 1945 THEN 'End of WWII'
        WHEN year = 1950 THEN 'Post-War Boom'
        WHEN year = 1975 THEN 'Oil Crisis Era'
        WHEN year = 2000 THEN 'Millennium'
        WHEN year = 2008 THEN 'Financial Crisis'
        WHEN year = 2020 THEN 'COVID-19'
        WHEN year = 2024 THEN 'Latest'
        ELSE NULL
    END as milestone
FROM yearly_summary
WHERE year IN (1900, 1945, 1950, 1975, 2000, 2008, 2019, 2020, 2021, 2024)
ORDER BY year;


-- ====================
-- 2. TOP POLLUTERS
-- ====================

-- Top 20 historical polluters (excluding regional aggregates)
SELECT 
    country,
    total_co2,
    latest_2024_co2,
    avg_co2_per_capita,
    ROUND((latest_2024_co2 / NULLIF(total_co2, 0)) * 100, 2) as pct_in_recent_year
FROM country_summary
WHERE country NOT LIKE '%(GCP)%'
    AND total_co2 > 1000
ORDER BY total_co2 DESC
LIMIT 20;


-- Top 15 per capita emitters with context
SELECT 
    country,
    avg_co2_per_capita,
    latest_2024_per_capita,
    total_co2,
    CASE 
        WHEN avg_co2_per_capita > 30 THEN 'Extreme'
        WHEN avg_co2_per_capita > 15 THEN 'Very High'
        WHEN avg_co2_per_capita > 8 THEN 'High'
        ELSE 'Moderate'
    END as emission_category
FROM country_summary
WHERE avg_co2_per_capita IS NOT NULL
ORDER BY avg_co2_per_capita DESC
LIMIT 15;


-- ====================
-- 3. COUNTRY CHANGES (2000-2024)
-- ====================

-- Biggest increases
WITH emissions_2000 AS (
    SELECT country, co2 as co2_2000
    FROM raw_emissions
    WHERE year = 2000 AND co2 IS NOT NULL
),
emissions_2024 AS (
    SELECT country, co2 as co2_2024
    FROM raw_emissions
    WHERE year = 2024 AND co2 IS NOT NULL
)
SELECT 
    e2000.country,
    ROUND(e2000.co2_2000, 2) as co2_2000,
    ROUND(e2024.co2_2024, 2) as co2_2024,
    ROUND(e2024.co2_2024 - e2000.co2_2000, 2) as absolute_change,
    ROUND(((e2024.co2_2024 - e2000.co2_2000) / e2000.co2_2000 * 100), 1) as change_pct
FROM emissions_2000 e2000
JOIN emissions_2024 e2024 ON e2000.country = e2024.country
WHERE e2000.co2_2000 > 100  -- Only significant emitters
ORDER BY change_pct DESC
LIMIT 20;


-- Countries that REDUCED emissions (2000-2024)
WITH emissions_2000 AS (
    SELECT country, co2 as co2_2000
    FROM raw_emissions
    WHERE year = 2000 AND co2 IS NOT NULL
),
emissions_2024 AS (
    SELECT country, co2 as co2_2024
    FROM raw_emissions
    WHERE year = 2024 AND co2 IS NOT NULL
)
SELECT 
    e2000.country,
    ROUND(e2000.co2_2000, 2) as co2_2000,
    ROUND(e2024.co2_2024, 2) as co2_2024,
    ROUND(e2024.co2_2024 - e2000.co2_2000, 2) as absolute_change,
    ROUND(((e2024.co2_2024 - e2000.co2_2000) / e2000.co2_2000 * 100), 1) as change_pct
FROM emissions_2000 e2000
JOIN emissions_2024 e2024 ON e2000.country = e2024.country
WHERE e2000.co2_2000 > 50  -- Only countries with meaningful baseline
    AND e2024.co2_2024 < e2000.co2_2000  -- Decreased
ORDER BY change_pct ASC
LIMIT 20;


-- ====================
-- 4. COVID-19 IMPACT
-- ====================

-- Global COVID impact
SELECT 
    year,
    total_global_co2,
    yoy_growth_rate,
    LAG(total_global_co2) OVER (ORDER BY year) as prev_year_co2,
    total_global_co2 - LAG(total_global_co2) OVER (ORDER BY year) as absolute_change
FROM yearly_summary
WHERE year BETWEEN 2018 AND 2024
ORDER BY year;


-- Country-level COVID impact (top 20 emitters)
WITH top_emitters AS (
    SELECT DISTINCT country
    FROM country_summary
    WHERE country NOT LIKE '%(GCP)%'
    ORDER BY total_co2 DESC
    LIMIT 20
)
SELECT 
    r.country,
    MAX(CASE WHEN r.year = 2019 THEN r.co2 END) as co2_2019,
    MAX(CASE WHEN r.year = 2020 THEN r.co2 END) as co2_2020,
    MAX(CASE WHEN r.year = 2021 THEN r.co2 END) as co2_2021,
    MAX(CASE WHEN r.year = 2024 THEN r.co2 END) as co2_2024,
    ROUND(
        (MAX(CASE WHEN r.year = 2020 THEN r.co2 END) - 
         MAX(CASE WHEN r.year = 2019 THEN r.co2 END)) / 
         NULLIF(MAX(CASE WHEN r.year = 2019 THEN r.co2 END), 0) * 100, 
        1
    ) as pct_drop_2020
FROM raw_emissions r
JOIN top_emitters te ON r.country = te.country
WHERE r.year IN (2019, 2020, 2021, 2024)
GROUP BY r.country
ORDER BY pct_drop_2020;


-- ====================
-- 5. GDP vs CO2 ANALYSIS
-- ====================

-- CO2 intensity (emissions per unit of GDP) - 2019 data
SELECT 
    country,
    co2,
    gdp,
    population,
    ROUND((co2 / NULLIF(gdp, 0)) * 1000000, 2) as co2_per_million_gdp,
    ROUND(co2_per_capita, 2) as co2_per_capita,
    CASE 
        WHEN (co2 / NULLIF(gdp, 0)) * 1000000 < 100 THEN 'Efficient'
        WHEN (co2 / NULLIF(gdp, 0)) * 1000000 < 300 THEN 'Moderate'
        ELSE 'Inefficient'
    END as efficiency_category
FROM raw_emissions
WHERE year = 2019 
    AND gdp IS NOT NULL 
    AND co2 IS NOT NULL
    AND gdp > 100000  -- Significant economies only
ORDER BY co2_per_million_gdp DESC
LIMIT 30;


-- Wealth vs emissions (per capita) - 2019
SELECT 
    country,
    ROUND(gdp / NULLIF(population, 0), 0) as gdp_per_capita,
    ROUND(co2_per_capita, 2) as co2_per_capita,
    co2,
    population
FROM raw_emissions
WHERE year = 2019 
    AND gdp IS NOT NULL 
    AND population > 1000000  -- Countries with significant population
ORDER BY gdp_per_capita DESC
LIMIT 50;


-- ====================
-- 6. REGIONAL ANALYSIS
-- ====================

-- Regional totals and averages
SELECT 
    country as region,
    total_co2,
    avg_annual_co2,
    avg_co2_per_capita,
    latest_2024_co2
FROM country_summary
WHERE country LIKE '%(GCP)%'
ORDER BY total_co2 DESC;


-- Regional time series (last 50 years)
SELECT 
    year,
    SUM(CASE WHEN country = 'Asia (GCP)' THEN co2 ELSE 0 END) as asia,
    SUM(CASE WHEN country = 'Europe (GCP)' THEN co2 ELSE 0 END) as europe,
    SUM(CASE WHEN country = 'North America (GCP)' THEN co2 ELSE 0 END) as north_america,
    SUM(CASE WHEN country = 'South America (GCP)' THEN co2 ELSE 0 END) as south_america,
    SUM(CASE WHEN country = 'Africa (GCP)' THEN co2 ELSE 0 END) as africa,
    SUM(CASE WHEN country = 'Oceania (GCP)' THEN co2 ELSE 0 END) as oceania
FROM raw_emissions
WHERE country LIKE '%(GCP)%'
    AND year >= 1975
GROUP BY year
ORDER BY year;


-- ====================
-- 7. DECADE COMPARISONS
-- ====================

-- Emissions by decade
SELECT 
    FLOOR(year / 10) * 10 as decade,
    ROUND(AVG(total_global_co2), 2) as avg_co2_per_year,
    ROUND(SUM(total_global_co2), 2) as total_decade_co2,
    ROUND(AVG(yoy_growth_rate), 2) as avg_growth_rate
FROM yearly_summary
WHERE year >= 1900
GROUP BY FLOOR(year / 10) * 10
ORDER BY decade;


-- ====================
-- 8. ANOMALY DETECTION
-- ====================

-- Years with unusual growth/decline
WITH stats AS (
    SELECT 
        AVG(yoy_growth_rate) as avg_growth,
        STDDEV(yoy_growth_rate) as std_growth
    FROM yearly_summary
    WHERE year >= 1950  -- Modern era only
)
SELECT 
    ys.year,
    ys.total_global_co2,
    ROUND(ys.yoy_growth_rate, 2) as growth_rate,
    ROUND(s.avg_growth, 2) as avg_growth,
    CASE 
        WHEN ys.yoy_growth_rate > s.avg_growth + (2 * s.std_growth) THEN 'Unusually High'
        WHEN ys.yoy_growth_rate < s.avg_growth - (2 * s.std_growth) THEN 'Unusually Low'
        ELSE 'Normal'
    END as anomaly_status
FROM yearly_summary ys
CROSS JOIN stats s
WHERE ys.year >= 1950
ORDER BY ys.year DESC;


-- ====================
-- 9. POPULATION-ADJUSTED TRENDS
-- ====================

-- Per capita trends for major countries
SELECT 
    year,
    MAX(CASE WHEN country = 'United States' THEN co2_per_capita END) as usa_per_capita,
    MAX(CASE WHEN country = 'China' THEN co2_per_capita END) as china_per_capita,
    MAX(CASE WHEN country = 'India' THEN co2_per_capita END) as india_per_capita,
    MAX(CASE WHEN country = 'Germany' THEN co2_per_capita END) as germany_per_capita,
    MAX(CASE WHEN country = 'Japan' THEN co2_per_capita END) as japan_per_capita,
    MAX(CASE WHEN country = 'United Kingdom' THEN co2_per_capita END) as uk_per_capita
FROM raw_emissions
WHERE country IN ('United States', 'China', 'India', 'Germany', 'Japan', 'United Kingdom')
    AND year >= 1950
    AND co2_per_capita IS NOT NULL
GROUP BY year
ORDER BY year;


-- ====================
-- 10. COMPARATIVE RANKINGS
-- ====================

-- Country rankings in 1990 vs 2024
WITH rank_1990 AS (
    SELECT 
        country,
        co2,
        ROW_NUMBER() OVER (ORDER BY co2 DESC) as rank_1990
    FROM raw_emissions
    WHERE year = 1990 AND co2 > 50
),
rank_2024 AS (
    SELECT 
        country,
        co2,
        ROW_NUMBER() OVER (ORDER BY co2 DESC) as rank_2024
    FROM raw_emissions
    WHERE year = 2024 AND co2 > 50
)
SELECT 
    COALESCE(r1990.country, r2024.country) as country,
    r1990.rank_1990,
    ROUND(r1990.co2, 2) as co2_1990,
    r2024.rank_2024,
    ROUND(r2024.co2, 2) as co2_2024,
    (r1990.rank_1990 - r2024.rank_2024) as rank_change,
    CASE 
        WHEN r1990.rank_1990 - r2024.rank_2024 > 0 THEN 'Climbed ▲'
        WHEN r1990.rank_1990 - r2024.rank_2024 < 0 THEN 'Dropped ▼'
        ELSE 'Same ='
    END as trend
FROM rank_1990 r1990
FULL OUTER JOIN rank_2024 r2024 ON r1990.country = r2024.country
WHERE r1990.rank_1990 <= 30 OR r2024.rank_2024 <= 30
ORDER BY r2024.rank_2024 NULLS LAST;


-- ====================
-- 11. DATA QUALITY CHECKS
-- ====================

-- Missing data by year
SELECT 
    year,
    COUNT(*) as total_records,
    SUM(CASE WHEN co2 IS NULL THEN 1 ELSE 0 END) as missing_co2,
    SUM(CASE WHEN gdp IS NULL THEN 1 ELSE 0 END) as missing_gdp,
    SUM(CASE WHEN population IS NULL THEN 1 ELSE 0 END) as missing_population,
    SUM(CASE WHEN co2_per_capita IS NULL THEN 1 ELSE 0 END) as missing_per_capita
FROM raw_emissions
GROUP BY year
ORDER BY year DESC
LIMIT 50;


-- Countries with most complete data
SELECT 
    country,
    COUNT(*) as total_years,
    SUM(CASE WHEN co2 IS NOT NULL THEN 1 ELSE 0 END) as years_with_co2,
    SUM(CASE WHEN gdp IS NOT NULL THEN 1 ELSE 0 END) as years_with_gdp,
    ROUND(SUM(CASE WHEN co2 IS NOT NULL THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 1) as co2_completeness_pct
FROM raw_emissions
WHERE country NOT LIKE '%(GCP)%'
GROUP BY country
ORDER BY co2_completeness_pct DESC, total_years DESC
LIMIT 30;


-- ====================
-- 12. ADVANCED: MOVING AVERAGES
-- ====================

-- 5-year moving average for top emitters
SELECT 
    country,
    year,
    co2 as actual_co2,
    ROUND(AVG(co2) OVER (
        PARTITION BY country 
        ORDER BY year 
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ), 2) as moving_avg_5yr
FROM raw_emissions
WHERE country IN ('United States', 'China', 'India', 'Russia', 'Japan')
    AND year >= 1990
    AND co2 IS NOT NULL
ORDER BY country, year;
