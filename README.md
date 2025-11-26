# CO2 Data Engineering Pipeline with ML Clustering

A complete data engineering pipeline for analyzing global CO2 emissions with **K-means clustering** using **Kafka, Spark, PostgreSQL, and Superset** deployed on **Kubernetes**.

## Project Overview

### Dataset
**Source:** Our World in Data - CO2 Emissions Dataset

| Aspect | Original | Processed |
|--------|----------|-----------|
| **Rows** | 50,407 | 23,405 (1900-2024 filtered) |
| **Columns** | 79 | 7 (selected variables) |
| **Size** | 14MB | 1.4MB |
| **Time Range** | 1750-2024 | 1900-2024 (125 years) |
| **Data Quality** | Sparse pre-1900 | Dense, complete |

### Selected Variables
1. `country` - Country name
2. `year` - Year (1900-2024)
3. `iso_code` - ISO 3-letter country code
4. `population` - Population
5. `gdp` - Gross Domestic Product
6. `co2` - Total CO2 emissions (million tonnes)
7. `co2_per_capita` - Per capita emissions (tonnes)

**Rationale**: Focused on time-series analysis, country comparisons, GDP-emissions correlation, and geographic visualizations. Pre-1900 data was removed due to significant gaps and missing values.

## Architecture

### Components
1. **Apache Kafka (KRaft mode)** - Message broker for streaming (no Zookeeper)
2. **Apache Spark (Master + Worker)** - ML clustering with K-means (k=3)
3. **PostgreSQL** - Storage for clustering results
4. **Apache Superset** - Data visualization dashboards

### Data Flow
```
CSV (23K rows) → Kafka Producer → Kafka Topic (emissions-topic)
                        ↓
                 Spark Consumer (K-means clustering, k=3)
                        ↓
                 PostgreSQL (co2_clusters, cluster_stats)
                        ↓
                 Superset Dashboards
```

**Key Features**:
- KRaft mode Kafka (no Zookeeper dependency)
- Real-time ML clustering in Spark
- Persistent storage with PostgreSQL
- Interactive dashboards with Superset
- Temporal context in clustering (first_year, last_year, avg_co2_recent)

## Database Schema

**Database**: `co2_emissions`
**Credentials**: `postgres` / `postgres`

### Tables

#### 1. `co2_clusters` (Main clustering results)
| Column | Type | Description |
|--------|------|-------------|
| `country` | text | Country name |
| `iso_code` | text | ISO 3-letter code |
| `avg_co2` | double precision | Average CO2 emissions (all years) |
| `avg_co2_per_capita` | double precision | Average per capita emissions |
| `avg_gdp` | double precision | Average GDP |
| `avg_population` | double precision | Average population |
| `data_points` | integer | Number of years with data |
| `first_year` | integer | Earliest year in dataset |
| `last_year` | integer | Latest year in dataset |
| `avg_co2_recent` | numeric(15,4) | Average CO2 since 2010 |
| `cluster` | integer | K-means cluster (0, 1, 2) |
| `batch_id` | integer | Processing batch ID |
| `processing_time` | timestamp | When record was saved |

#### 2. `cluster_stats` (Aggregated statistics per cluster)
| Column | Type | Description |
|--------|------|-------------|
| `cluster` | integer | Cluster number (0, 1, 2) |
| `num_countries` | integer | Number of countries in cluster |
| `avg_co2_cluster` | double precision | Average CO2 for cluster |
| `avg_co2_per_capita_cluster` | double precision | Average per capita for cluster |
| `avg_gdp_cluster` | double precision | Average GDP for cluster |
| `batch_id` | integer | Processing batch ID |
| `processing_time` | timestamp | When record was saved |

### Views
- **cluster_analysis** - Comprehensive cluster statistics
- **top_emitters_by_cluster** - Top 10 emitters per cluster

## Project Structure

```
miacd-iacd-data-pipeline/
├── README.md                    # Complete setup guide
├── SUPERSET_SETUP.md            # Superset configuration guide
├── LOGICA_CONSUMER.md           # Detailed consumer logic explanation
├── MELHORIAS_TEMPORAL.md        # Temporal context improvements
├── REFATORACAO_CONSUMER.md      # Consumer refactoring documentation
├── requirements.txt             # Python dependencies (for local dev/Jupyter)
├── data/
│   ├── owid-co2-data.csv        # Original dataset (14MB, 79 columns)
│   └── reduced_co2.csv          # Processed: 7 columns, 23K rows (1900-2024)
├── scripts/
│   ├── eda.ipynb                # Exploratory data analysis
│   └── extract_reduced.py       # Dataset extraction script
├── kafka/
│   ├── Dockerfile               # Kafka producer container image
│   └── producer.py              # Streams CSV → Kafka topic
├── spark/
│   ├── Dockerfile               # Spark consumer container image  
│   └── consumer.py              # Kafka → Clean → Aggregate → K-means → PostgreSQL
├── superset/
│   └── Dockerfile               # Custom Superset image with PostgreSQL driver
├── postgres/
│   └── init.sql                 # Database schema (tables, views, indexes)
└── kubernetes/                  # K8s deployment manifests (01-07)
    ├── 01-postgres.yaml         # PostgreSQL (PVC, ConfigMap, Deployment, Service)
    ├── 02-kafka.yaml            # Kafka KRaft (Service Headless, StatefulSet)
    ├── 03-spark-master.yaml     # Spark master (Service, Deployment)
    ├── 04-spark-worker.yaml     # Spark worker (Deployment)
    ├── 05-kafka-producer.yaml   # Kafka producer (Deployment)
    ├── 06-spark-consumer.yaml   # Spark consumer (Deployment)
    └── 07-superset.yaml         # Superset (Service, PVC, Deployment)
```

## Usage

### Prerequisites
- Minikube installed
- kubectl configured
- Docker
- Python 3.8+ with pip (for local development)

### Deployment Steps

1. **Start Minikube**
   ```bash
   minikube start --cpus=4 --memory=8192
   ```

2. **Configure Docker Environment for Minikube**
   ```bash
   eval $(minikube docker-env)
   ```

3. **Build Docker Images**
   ```bash
   # Build Kafka producer
   docker build -t kafka-producer:latest ./kafka
   
   # Build Spark consumer
   docker build -t spark-consumer:latest ./spark
   
   # Build Superset with PostgreSQL driver (REQUIRED!)
   docker build -t superset-postgres:v2 ./superset
   ```
   
   **Important**: The Superset image MUST be built locally because the official `apache/superset:latest` does NOT include database drivers. Our custom image installs the PostgreSQL driver (`psycopg2-binary`).

4. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f kubernetes/
   ```

5. **Verify Deployment**
   Wait for all pods to be in `Running` state:
   ```bash
   kubectl get pods
   
   # Expected pods:
   # - kafka-0
   # - kafka-producer-xxx
   # - postgres-xxx
   # - spark-consumer-xxx
   # - spark-master-xxx
   # - spark-worker-xxx
   # - superset-xxx
   ```

### Verification

Check logs to ensure data is flowing:
```bash
# Kafka Producer
kubectl logs deployment/kafka-producer --tail=20

# Spark Consumer
kubectl logs deployment/spark-consumer --tail=50

# PostgreSQL Data
kubectl exec deployment/postgres -- psql -U postgres -d co2_emissions -c \
  "SELECT COUNT(*) FROM co2_clusters;"
```

### Accessing Services

#### Superset Dashboard (Data Visualization)

**⚠️ IMPORTANT: You MUST keep the port-forward terminal open while using Superset!**

1. **Start Port-Forward**:
   ```bash
   kubectl port-forward service/superset 8088:8088
   ```
   Leave this terminal open.

2. **Access Superset**:
   - URL: `http://localhost:8088`
   - Login: `admin` / `admin`

3. **Connect to PostgreSQL Database**:
   - Settings → Data: Database Connections → + DATABASE
   - Select **PostgreSQL**
   - **SQLALCHEMY URI**: 
     ```
     postgresql://postgres:postgres@postgres:5432/co2_emissions
     ```
   - Advanced → SQL Lab → Enable all options
   - Click **TEST CONNECTION** → should show ✅ "Connection looks good!"
   - Click **CONNECT**

4. **Add Datasets** (Data → Datasets → + Dataset):
   - `co2_clusters` - Main clustering results
   - `cluster_stats` - Aggregated cluster statistics
   - `cluster_analysis` - Comprehensive cluster view

5. **Create Dashboards**:
   See detailed instructions in [`SUPERSET_SETUP.md`](SUPERSET_SETUP.md)

**Troubleshooting**:
- If connection fails: verify port-forward is running (`kubectl port-forward service/superset 8088:8088`)
- If "Could not load database driver" error: rebuild Superset image with `docker build -t superset-postgres:v2 ./superset`

#### Spark Master UI
```bash
kubectl port-forward service/spark-master 8080:8080
# Access at http://localhost:8080
```

## Spark Consumer Processing

The consumer applies the following transformations:

1. **Data Cleaning** (`clean_data`):
   - Convert string "NaN" to NULL for numeric columns
   - Filter aggregate records (World, continents, etc.)

2. **Country Aggregation** (`aggregate_by_country`):
   - Group by country and ISO code
   - Calculate averages: CO2, CO2 per capita, GDP, population
   - Add temporal context:
     - `data_points`: Number of years
     - `first_year`: Earliest year
     - `last_year`: Latest year
     - `avg_co2_recent`: Average CO2 since 2010

3. **Clustering** (`perform_clustering`):
   - Features: avg_co2, avg_co2_per_capita, avg_gdp, avg_population
   - StandardScaler normalization
   - K-means (k=3, seed=42, maxIter=20)

4. **Cluster Statistics** (`calculate_cluster_stats`):
   - Aggregate metrics per cluster
   - Countries per cluster, average values

5. **Save to PostgreSQL**:
   - `co2_clusters` table
   - `cluster_stats` table

See [`LOGICA_CONSUMER.md`](LOGICA_CONSUMER.md) for detailed explanation.

## ML Clustering Details

### K-means Configuration
- **Number of clusters (k)**: 3
- **Features used**: avg_co2, avg_co2_per_capita, avg_gdp, avg_population
- **Pre-processing**: StandardScaler (feature normalization)
- **Algorithm**: K-means clustering in PySpark MLlib
- **Seed**: 42 (for reproducibility)
- **Max iterations**: 20

### Expected Cluster Patterns
- **Cluster 0**: Developing countries (low CO2, low GDP)
- **Cluster 1**: Moderate emitters (medium CO2, medium GDP)
- **Cluster 2**: Industrialized countries (high CO2, high GDP, high per capita)

## Useful Commands

### Kafka
```bash
# List topics
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Monitor messages (first 10)
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic emissions-topic \
  --from-beginning --max-messages 10
```

### PostgreSQL
```bash
# Access database
kubectl exec -it deployment/postgres -- psql -U postgres -d co2_emissions

# Useful queries:
SELECT COUNT(*) FROM co2_clusters;
SELECT cluster, COUNT(*) as countries FROM co2_clusters GROUP BY cluster;
SELECT * FROM cluster_analysis;
```

### Restart Components
```bash
kubectl rollout restart deployment/kafka-producer
kubectl rollout restart deployment/spark-consumer
kubectl rollout restart deployment/superset
```

### Stop and Resume
```bash
# Stop (keeps data)
minikube stop

# Resume
minikube start
kubectl port-forward service/superset 8088:8088  # If needed

# Clean everything
kubectl delete -f kubernetes/
minikube delete
```

## Troubleshooting

### Pods in ImagePullBackOff
```bash
# Verify images were built:
eval $(minikube docker-env)
docker images | grep -E "kafka-producer|spark-consumer|superset"

# Rebuild if necessary
docker build -t kafka-producer:latest ./kafka
docker build -t spark-consumer:latest ./spark
docker build -t superset-postgres:v2 ./superset
```

### Superset Not Starting
```bash
# Check logs
kubectl logs deployment/superset

# Restart
kubectl rollout restart deployment/superset
```

### Consumer Not Processing Data
```bash
# Verify Kafka is running
kubectl get pods | grep kafka

# Check consumer logs
kubectl logs deployment/spark-consumer --tail=50

# Verify PostgreSQL
kubectl exec deployment/postgres -- psql -U postgres -d co2_emissions -c \
  "SELECT COUNT(*) FROM co2_clusters;"
```

### Adding Missing Columns to PostgreSQL
If upgrading from older version:
```bash
kubectl exec deployment/postgres -- psql -U postgres -d co2_emissions -c \
  "ALTER TABLE co2_clusters ADD COLUMN IF NOT EXISTS data_points INTEGER;
   ALTER TABLE co2_clusters ADD COLUMN IF NOT EXISTS first_year INTEGER;
   ALTER TABLE co2_clusters ADD COLUMN IF NOT EXISTS last_year INTEGER;
   ALTER TABLE co2_clusters ADD COLUMN IF NOT EXISTS avg_co2_recent DECIMAL(15,4);"
```

## Documentation

Additional documentation files:
- **[LOGICA_CONSUMER.md](LOGICA_CONSUMER.md)** - Detailed Spark consumer logic
- **[MELHORIAS_TEMPORAL.md](MELHORIAS_TEMPORAL.md)** - Temporal context improvements
- **[REFATORACAO_CONSUMER.md](REFATORACAO_CONSUMER.md)** - Consumer refactoring
- **[AUDITORIA_KUBERNETES.md](AUDITORIA_KUBERNETES.md)** - Kubernetes manifests audit
- **[SUPERSET_SETUP.md](SUPERSET_SETUP.md)** - Superset configuration guide

## Technology Stack

- **Kubernetes** - Container orchestration
- **Apache Kafka 4.1.0** - Streaming platform (KRaft mode)
- **Apache Spark 4.0.1** - Distributed processing + MLlib
- **PostgreSQL 15** - Relational database
- **Apache Superset** - Business intelligence and visualization
- **Python 3.11** - Programming language
- **Docker** - Containerization

## Project Status

### Completed
- ✅ Dataset reduced from 79 → 7 columns (1900-2024, 23,405 rows)
- ✅ KRaft Kafka deployment (no Zookeeper)
- ✅ Kafka producer streaming CSV data
- ✅ Spark K-means clustering consumer (k=3) with temporal context
- ✅ PostgreSQL schema with clustering tables
- ✅ Consolidated Kubernetes manifests (7 files)
- ✅ Modular consumer code (6 focused functions)
- ✅ All pods deployed and running
- ✅ Superset dashboards operational

### Architecture Highlights
- **Simplified**: KRaft mode eliminates Zookeeper complexity
- **ML Integration**: Real-time K-means clustering in Spark
- **Temporal Context**: first_year, last_year, avg_co2_recent for trend analysis
- **Scalable**: Kubernetes orchestration with persistent storage
- **Modular**: Clean, testable consumer code
- **Modern**: Latest versions of Kafka, Spark, PostgreSQL

## Contributors

**Course**: IACD (Infraestruturas e Arquiteturas para Ciência de Dados)  
**Project**: Data Engineering Pipeline with Machine Learning  
**Technology Stack**: Kafka + Spark + PostgreSQL + Superset on Kubernetes  

---

**Last Updated**: November 26, 2025
