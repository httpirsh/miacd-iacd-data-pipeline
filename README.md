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
3. **PostgreSQL** - Storage for raw data and clustering results
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

## Database Schema

**Database**: `co2_emissions`
**Credentials**: `postgres` / `postgres`

### Tables
1. **co2_clusters** (ML results)
   - batch_id, country, year_min, year_max, records
   - avg_population, avg_gdp, avg_co2, avg_co2_per_capita
   - cluster (0, 1, or 2 from K-means)
   
2. **cluster_stats** (aggregated by cluster)
   - cluster, country_count, total_records
   - avg_population, avg_gdp, avg_co2, avg_co2_per_capita

### Views
- **cluster_analysis** - Comprehensive cluster statistics

## Project Structure

```
project/
├── README.md                    # Complete setup guide
├── SUPERSET_SETUP.md            # Superset configuration guide
├── requirements.txt             # Python dependencies (for local dev/Jupyter)
├── data/
│   ├── owid-co2-data.csv        # Original dataset (14MB, 79 columns)
│   └── reduced_co2.csv          # Processed: 7 columns, ~19K rows (1950-2024)
├── scripts/
│   ├── eda.ipynb                # Exploratory data analysis
│   └── extract_reduced.py       # Dataset extraction script
├── kafka/
│   ├── Dockerfile               # Kafka producer container image
│   └── producer.py              # Streams CSV → Kafka topic
├── spark/
│   ├── Dockerfile               # Spark consumer container image  
│   └── consumer.py              # Kafka → NaN cleaning → K-means → PostgreSQL
├── superset/
│   └── Dockerfile               # ⚠️ CUSTOM Superset image with PostgreSQL driver
├── postgres/
│   └── init.sql                 # Database schema (co2_clusters, cluster_stats)
└── kubernetes/                  # K8s deployment manifests (01-09)
    ├── 01-postgres-pvc.yaml     # Persistent storage for PostgreSQL
    ├── 02-postgres-deploy.yaml  # PostgreSQL deployment
    ├── 03-postgres-service.yaml # PostgreSQL service
    ├── 04-kafka-kraft.yaml      # Kafka (KRaft mode, no Zookeeper)
    ├── 05-spark-master.yaml     # Spark master deployment
    ├── 06-spark-worker.yaml     # Spark worker deployment
    ├── 07-superset.yaml         # Superset with custom image (superset-postgres:v2)
    ├── 08-kafka-producer.yaml   # Containerized Kafka producer
    └── 09-spark-consumer.yaml   # Containerized Spark consumer
```

## Usage

### Prerequisites
- Minikube installed
- kubectl configured
- Python 3.8+ with pip
- Git

### Deployment Steps

1. **Start Minikube**
   ```bash
   minikube start --cpus=4 --memory=8192
   ```

2. **Build Docker Images**
   ```bash
   eval $(minikube docker-env)
   
   # Build Kafka producer
   docker build -t kafka-producer:latest -f kafka/Dockerfile .
   
   # Build Spark consumer
   docker build -t spark-consumer:latest -f spark/Dockerfile .
   
   # Build Superset with PostgreSQL driver (REQUIRED!)
   docker build -t superset-postgres:v2 ./superset
   ```
   
   **Important**: The Superset image MUST be built locally because the official `apache/superset:latest` does NOT include database drivers. Our custom image installs the PostgreSQL driver (`psycopg2-binary`) in the correct virtual environment.

3. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f kubernetes/
   ```

4. **Verify Deployment**
   Wait for all pods to be in `Running` state:
   ```bash
   kubectl get pods -w
   ```

### Verification
Check logs to ensure data is flowing:
```bash
# Kafka Producer
kubectl logs -l app=kafka-producer --tail=20

# Spark Consumer
kubectl logs -l app=spark-consumer --tail=50

# PostgreSQL Data
kubectl exec -it $(kubectl get pods -l app=postgres -o name | head -1) -- \
  psql -U postgres -d co2_emissions -c "SELECT COUNT(*) FROM co2_clusters;"
```

### Accessing Services

#### Superset Dashboard (Data Visualization)

**⚠️ IMPORTANT: You MUST keep the port-forward terminal open while using Superset!**

1. **Start Port-Forward**:
   ```bash
   kubectl port-forward svc/superset 8088:8088
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
- If connection fails: verify both port-forwards are running (Superset 8088, PostgreSQL 5432)
- If "Could not load database driver" error: rebuild Superset image with `docker build -t superset-postgres:v2 ./superset`

#### Spark Master UI
```bash
kubectl port-forward svc/spark-master 8080:8080
# Access at http://localhost:8080
```

## Useful Commands

### Kafka
```bash
# List topics
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Monitor messages
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic emissions-topic --from-beginning --max-messages 10
```

### PostgreSQL
```bash
# Connect to database
PGPASSWORD=postgres psql -h localhost -U postgres -d co2_emissions
```

## ML Clustering Details

### K-means Configuration
- **Number of clusters (k)**: 3
- **Features used**: avg_population, avg_gdp, avg_co2, avg_co2_per_capita
- **Algorithm**: K-means clustering in PySpark MLlib
- **Output**: Countries grouped by emission patterns

### Expected Cluster Patterns
- **Cluster 0**: High population, moderate emissions
- **Cluster 1**: Low population, low emissions  
- **Cluster 2**: High GDP, high per capita emissions

## Troubleshooting

- **Kafka not receiving messages**: Check topic existence and producer logs. Ensure CSV path is correct.
- **Spark consumer not processing**: Verify PostgreSQL is running and Spark packages are downloaded.
- **PostgreSQL connection**: Use `postgres` host within K8s, `localhost` with port-forward.
- **PVC issues**: If stuck terminating, remove finalizers. Check Minikube disk space.
- **OOM Errors**: Increase Minikube memory or adjust Spark worker config.

## Project Status

### Completed
- Dataset reduced from 79 → 7 columns (1900-2024, 23,405 rows)
- KRaft Kafka deployment (no Zookeeper)
- Kafka producer streaming CSV data
- Spark K-means clustering consumer (k=3)
- PostgreSQL schema with clustering tables
- All 6 Kubernetes pods deployed and running
- Port-forwards active (Kafka 9092, PostgreSQL 5432, Superset 8088)

### Architecture Highlights
- **Simplified**: KRaft mode eliminates Zookeeper complexity
- **ML Integration**: Real-time K-means clustering in Spark
- **Scalable**: Kubernetes orchestration with persistent storage
- **Modern**: kafka-python-ng for Python 3.12+ compatibility

## Contributors

**IACD** - Data Engineering Pipeline Project  
**Technology Stack**: Kafka + Spark + PostgreSQL + Superset on Kubernetes  
**Repository**: [miacd-iacd-data-pipeline](https://github.com/httpirsh/miacd-iacd-data-pipeline)

---

**Last Updated**: November 25, 2025
