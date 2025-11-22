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
├── README.md                   # This file - Complete setup guide
├── data/
│   ├── owid-co2-data.csv       # Original dataset (14MB)
│   └── reduced_co2.csv         # 7 columns, 23,405 rows (1900-2024)
├── scripts/
│   ├── eda.ipynb               # Exploratory data analysis
│   └── extract_reduced.py      # Dataset extraction (1900-2024)
├── kafka/
│   └── producer.py             # Stream CSV to emissions-topic
├── spark/
│   └── consumer.py             # Kafka → K-means → PostgreSQL
├── postgres/
│   └── init.sql                # Database schema with clustering tables
└── kubernetes/                 # Deployment manifests (01-07)
    ├── 01-postgres-pvc.yaml
    ├── 02-postgres-deploy.yaml
    ├── 03-postgres-service.yaml
    ├── 04-kafka-kraft.yaml
    ├── 05-spark-master.yaml
    ├── 06-spark-worker.yaml
    └── 07-superset.yaml
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

### Step 2: Deploy Kubernetes Components
```bash
cd /home/IACD/project/kubernetes

# Deploy in order (01-07)
kubectl apply -f 01-postgres-pvc.yaml
kubectl apply -f 02-postgres-deploy.yaml
kubectl apply -f 03-postgres-service.yaml
kubectl apply -f 04-kafka-kraft.yaml
kubectl apply -f 05-spark-master.yaml
kubectl apply -f 06-spark-worker.yaml
kubectl apply -f 07-superset.yaml
```

---

### Step 3: Wait for All Pods to be Ready
```bash
kubectl get pods -w
# Wait until all 6 pods show "Running" (1-2 minutes)
# Expected pods: kafka-0, postgres-0, postgres-xxx, spark-master-xxx, spark-worker-xxx, superset-xxx
```

---

### Step 4: Initialize PostgreSQL Database
```bash
# Port-forward PostgreSQL
kubectl port-forward postgres-0 5432:5432 &

# Wait 5 seconds, then initialize schema
sleep 5
PGPASSWORD=postgres psql -h localhost -U postgres -d co2_emissions -f postgres/init.sql
```

---

### Step 5: Install Python Dependencies
```bash
cd /home/IACD/project
pip install kafka-python-ng pandas psycopg2-binary
```

---

### Step 6: Create Kafka Topic
```bash
# Port-forward Kafka
kubectl port-forward kafka-0 9092:9092 &

# Wait 5 seconds, then create topic
sleep 5
kubectl exec kafka-0 -- /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic emissions-topic \
  --partitions 3 --replication-factor 1
```

---

### Step 7: Start Kafka Producer (Streaming Data)
```bash
cd /home/IACD/project/kafka
python producer.py
# You should see: "sent: Afghanistan - 1949 ✓"
# Leave this running in the background or press Ctrl+C after a few hundred records
```

---

### Step 8: Run Spark Consumer (ML Clustering)
```bash
# Get Spark master pod name
SPARK_POD=$(kubectl get pods -l app=spark-master -o jsonpath='{.items[0].metadata.name}')

# Copy consumer script to pod
kubectl cp spark/consumer.py $SPARK_POD:/tmp/consumer.py

# Submit Spark job for K-means clustering
kubectl exec $SPARK_POD -- spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /tmp/consumer.py
```

---

### Step 9: Verify Data in PostgreSQL
```bash
# Connect to database
PGPASSWORD=postgres psql -h localhost -U postgres -d co2_emissions

# Check clustering results
SELECT COUNT(*) FROM co2_clusters;
SELECT * FROM cluster_stats;
SELECT * FROM cluster_analysis;
```

---

### Step 10: Access Superset for Visualization
```bash
# Port-forward Superset (if not already running)
kubectl port-forward svc/superset 8088:8088 &

# Open browser
# URL: http://localhost:8088
# Default credentials: admin / admin
```

**Add PostgreSQL connection in Superset:**
- Host: `postgres.default.svc.cluster.local`
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
