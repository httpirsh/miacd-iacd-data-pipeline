# Consumer Logic

## Overview

The consumer reads data from Kafka, groups by country, applies K-means clustering, and saves to PostgreSQL.

```
Kafka → Spark → Clean data → Group by country → K-means (3 clusters) → PostgreSQL
```

## Main steps

### 1. Read from Kafka

Connects to Kafka and reads JSON messages from `emissions-topic` every 15 seconds.

### 2. Parsing and cleaning

- Converts JSON to DataFrame
- Removes "NaN" values (string from Pandas)
- Filters out aggregates (World, Africa, etc.) - we only want countries with valid `iso_code`

### 3. Country aggregation

Groups by country and calculates averages:
- Total CO2
- CO2 per capita
- GDP (kept for context/reporting, not used as a clustering feature)
- Population

Only keeps countries with ≥5 records.

### 4. Clustering

- **VectorAssembler**: combines 3 features into a vector — avg CO2, avg CO2 per capita, avg population
- **StandardScaler**: normalizes values (population is a much larger scale than the CO2 metrics, so it would otherwise dominate distance calculations)
- **K-means (k=3)**: groups countries into 3 clusters
- **Relabeling**: K-means assigns arbitrary cluster IDs (0/1/2 in no particular order), so clusters are re-sorted by their average CO2 and remapped to `0=Low`, `1=Mid`, `2=High` — this keeps labels consistent and meaningful across every streaming batch

Typical result:
- Cluster 0 (Low): low-emission countries
- Cluster 1 (Mid): medium-emission countries
- Cluster 2 (High): high-emission countries

### 5. Save to PostgreSQL

Two tables:
- `co2_clusters`: each country with its cluster
- `cluster_stats`: average statistics per cluster
