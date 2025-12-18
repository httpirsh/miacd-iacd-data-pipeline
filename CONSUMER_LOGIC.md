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
- GDP
- Population

Only keeps countries with ≥5 records.

### 4. Clustering

- **VectorAssembler**: combines the 4 features into a vector
- **StandardScaler**: normalizes values (otherwise GDP dominates since it's much larger)
- **K-means (k=3)**: groups countries into 3 clusters

Typical result:
- Cluster 0: low CO2/GDP countries
- Cluster 1: medium countries
- Cluster 2: high CO2/GDP countries

### 5. Save to PostgreSQL

Two tables:
- `co2_clusters`: each country with its cluster
- `cluster_stats`: average statistics per cluster
