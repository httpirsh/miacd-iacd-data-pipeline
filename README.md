# CO2 Data Engineering Pipeline with ML Clustering

A complete data engineering pipeline for analyzing global CO2 emissions with **K-means clustering** using **Kafka, Spark, PostgreSQL, and Superset** deployed on **Kubernetes**.

---

## 📊 Project Overview

### Dataset
**Source:** Our World in Data - CO2 Emissions Dataset

| Aspect | Original | Processed |
|--------|----------|-----------|
| **Rows** | 50,407 | 23,405 (1900-2024 filtered) |
| **Columns** | 79 | 7 (selected variables) |
| **Size** | 14MB | 1.4MB |
| **Time Range** | 1750-2024 | 1900-2024 (125 years) |
| **Data Quality** | Sparse pre-1900 | Dense, complete |

### Selected Variables (7 columns)
1. `country` - Country name
2. `year` - Year (1900-2024)
3. `iso_code` - ISO 3-letter country code
4. `population` - Population
5. `gdp` - Gross Domestic Product
6. `co2` - Total CO2 emissions (million tonnes)
7. `co2_per_capita` - Per capita emissions (tonnes)

**Rationale**: Focused on time-series analysis, country comparisons, GDP-emissions correlation, and geographic visualizations. Pre-1900 data was removed due to significant gaps and missing values.

---

## 🏗️ Architecture

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

---

## 📂 Database Schema

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

---

## 📁 Project Structure

```
project/
├── README.md                    # Complete setup guide with NaN handling
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
├── postgres/
│   ├── Dockerfile               # PostgreSQL with init script
│   └── init.sql                 # Database schema (co2_clusters, cluster_stats)
└── kubernetes/                  # K8s deployment manifests (01-09)
    ├── 01-postgres-pvc.yaml     # Persistent storage for PostgreSQL
    ├── 02-postgres-deploy.yaml  # PostgreSQL deployment
    ├── 03-postgres-service.yaml # PostgreSQL service
    ├── 04-kafka-kraft.yaml      # Kafka (KRaft mode, no Zookeeper)
    ├── 05-spark-master.yaml     # Spark master deployment
    ├── 06-spark-worker.yaml     # Spark worker deployment
    ├── 07-superset.yaml         # Superset visualization
    ├── 08-kafka-producer.yaml   # Containerized Kafka producer
    └── 09-spark-consumer.yaml   # Containerized Spark consumer
```


---

## 🚀 Quick Start Guide

### Prerequisites
- Minikube installed
- kubectl configured
- Python 3.8+ with pip
- Git

---

### Step 1: Start Minikube
```bash
minikube start --cpus=4 --memory=8192
```

---

### Step 2: Build Docker Images
```bash
# Switch to Minikube's Docker daemon
eval $(minikube docker-env)

# Build Kafka Producer image
docker build -t kafka-producer:latest -f kafka/Dockerfile .

# Build Spark Consumer image  
docker build -t spark-consumer:latest -f spark/Dockerfile .
```

---

### Step 3: Deploy All Kubernetes Components
```bash
# Deploy all manifests at once
kubectl apply -f kubernetes/

# Or deploy in order (01-09)
kubectl apply -f kubernetes/01-postgres-pvc.yaml
kubectl apply -f kubernetes/02-postgres-deploy.yaml
kubectl apply -f kubernetes/03-postgres-service.yaml
kubectl apply -f kubernetes/04-kafka-kraft.yaml
kubectl apply -f kubernetes/05-spark-master.yaml
kubectl apply -f kubernetes/06-spark-worker.yaml
kubectl apply -f kubernetes/07-superset.yaml
kubectl apply -f kubernetes/08-kafka-producer.yaml
kubectl apply -f kubernetes/09-spark-consumer.yaml
```

---

### Step 4: Wait for All Pods to be Running
```bash
kubectl get pods -w
# Wait until ALL 7 pods show "Running" (1-3 minutes)
# Expected pods:
#  - kafka-0
#  - postgres-xxxxx
#  - spark-master-xxxxx
#  - spark-worker-xxxxx  
#  - superset-xxxxx
#  - kafka-producer-xxxxx
#  - spark-consumer-xxxxx
```

---

### Step 5: Verify Data Pipeline is Working
```bash
# Check Kafka producer logs (should see "sent: Country - Year")
kubectl logs -l app=kafka-producer --tail=20

# Check Spark consumer logs (should see "processing batch X with Y records")
kubectl logs -l app=spark-consumer --tail=50

# Verify data in PostgreSQL
kubectl exec -it $(kubectl get pods -l app=postgres -o name | head -1) -- \
  psql -U postgres -d co2_emissions -c "\dt"

# Should see tables: co2_clusters, cluster_stats, debug_country_stats
kubectl exec -it $(kubectl get pods -l app=postgres -o name | head -1) -- \
  psql -U postgres -d co2_emissions -c "SELECT COUNT(*) FROM co2_clusters;"
```

---

### Step 6: Access Superset for Visualization
```bash
# Port-forward Superset
kubectl port-forward svc/superset 8088:8088

# Open browser: http://localhost:8088
# Default credentials: admin / admin
```

**Add PostgreSQL connection in Superset:**
- Host: `postgres` (service name in Kubernetes)
- Port: `5432`  
- Database: `co2_emissions`
- Username: `postgres`
- Password: `postgres`

---

## 🔧 Useful Commands

---

## 🔧 Useful Commands

### Check Pod Status
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name> --follow
```

### Kafka Commands
```bash
# List topics
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh \
  --list --bootstrap-server localhost:9092

# Monitor messages
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic emissions-topic \
  --from-beginning \
  --max-messages 10

# Check consumer groups
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --all-groups
```

### PostgreSQL Commands
```bash
# Connect to database
PGPASSWORD=postgres psql -h localhost -U postgres -d co2_emissions

# Useful queries
SELECT COUNT(*) FROM co2_clusters;
SELECT * FROM cluster_stats ORDER BY cluster;
SELECT * FROM cluster_analysis;
```

### Spark Commands
```bash
# Port-forward Spark Master UI
kubectl port-forward svc/spark-master 8080:8080 &
# Open http://localhost:8080

# Check Spark logs
kubectl logs -l app=spark-master --follow
kubectl logs -l app=spark-worker --follow
```

---

## 🧪 ML Clustering Details

### K-means Configuration
- **Number of clusters (k)**: 3
- **Features used**: avg_population, avg_gdp, avg_co2, avg_co2_per_capita
- **Algorithm**: K-means clustering in PySpark MLlib
- **Output**: Countries grouped by emission patterns

### Expected Cluster Patterns
- **Cluster 0**: High population, moderate emissions
- **Cluster 1**: Low population, low emissions  
- **Cluster 2**: High GDP, high per capita emissions

---

## 🛠️ Troubleshooting

---

## 🛠️ Troubleshooting

### Kafka not receiving messages
- Check if topic exists: `kubectl exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092`
- Verify port-forward is active: `netstat -an | grep 9092`
- Check producer logs for connection errors
- Ensure CSV path is correct: `../data/reduced_co2.csv` when running from `kafka/` directory

### Spark consumer not processing
- Check PostgreSQL is running: `kubectl get pods | grep postgres`
- Verify Spark packages downloaded: Check logs for "org.apache.spark:spark-sql-kafka"
- Monitor Spark Master UI: `kubectl port-forward svc/spark-master 8080:8080`
- Check consumer logs: `kubectl logs <spark-master-pod> --follow`

### PostgreSQL connection issues
- Use correct credentials: `postgres` / `postgres` (not co2_user)
- Database name: `co2_emissions` (not co2_data)
- For Superset, use internal hostname: `postgres.default.svc.cluster.local`
- For local access, ensure port-forward is active: `kubectl port-forward postgres-0 5432:5432`

### PVC (storage) issues
- If PVC stuck in "Terminating": `kubectl patch pvc <pvc-name> -p '{"metadata":{"finalizers":null}}'`
- Cannot shrink PVC size (only increase allowed)
- Check Minikube has enough disk: `minikube ssh "df -h"`

### Out of memory errors
- Increase Minikube resources: `minikube start --cpus=4 --memory=8192`
- Current Spark config: 512Mi per worker (adjust in `06-spark-worker.yaml` if needed)

### Pod stuck in CrashLoopBackOff
- Check logs: `kubectl logs <pod-name> --previous`
- Describe pod: `kubectl describe pod <pod-name>`
- Common causes: Wrong image version, missing dependencies, insufficient resources

### kafka-python compatibility issues
- Use `kafka-python-ng` (not kafka-python): `pip install kafka-python-ng`
- kafka-python 2.0.2 has Python 3.12 compatibility issues
- kafka-python-ng 2.2.3 is the maintained fork

---

## 🎯 Project Status

### Completed ✅
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

---

## 📚 Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark MLlib Guide](https://spark.apache.org/docs/latest/ml-clustering.html)
- [Superset Documentation](https://superset.apache.org/docs/intro)
- [Dataset Source](https://github.com/owid/co2-data)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [KRaft Mode](https://kafka.apache.org/documentation/#kraft)

---

## 👥 Contributors

**IACD** - Data Engineering Pipeline Project  
**Technology Stack**: Kafka + Spark + PostgreSQL + Superset on Kubernetes  
**Repository**: [miacd-iacd-data-pipeline](https://github.com/httpirsh/miacd-iacd-data-pipeline)

---

**Last Updated**: November 22, 2025
