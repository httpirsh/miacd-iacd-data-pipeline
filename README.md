# CO2 Data Engineering Pipeline

A complete data engineering pipeline for analyzing global CO2 emissions using **Kafka, Spark, PostgreSQL, and Superset** deployed on **Kubernetes**.

---

## 📊 Project Overview

### Dataset
**Source:** Our World in Data - CO2 Emissions Dataset

| Aspect | Original | Processed |
|--------|----------|-----------|
| **Rows** | 50,407 | 23,405 (1900-2014 filtered) |
| **Columns** | 79 | 7 (selected variables) |
| **Size** | 14MB | 1.4MB |
| **Time Range** | 1750-2014 | 1900-2014 (115 years) |
| **Data Quality** | Sparse pre-1900 | Dense, complete |

### Selected Variables (7 columns)
1. `country` - Country name
2. `year` - Year (1900-2014)
3. `iso_code` - ISO 3-letter country code
4. `population` - Population
5. `gdp` - Gross Domestic Product
6. `co2` - Total CO2 emissions (million tonnes)
7. `co2_per_capita` - Per capita emissions (tonnes)

**Rationale**: Focused on time-series analysis, country comparisons, GDP-emissions correlation, and geographic visualizations. Pre-1900 data was removed due to significant gaps and missing values.

---

## 🏗️ Architecture

### Components
1. **Apache Kafka** (KRaft mode) - Message broker for streaming
2. **Apache Spark** (Master + Worker) - Data processing engine
3. **PostgreSQL** - Relational database for storage
4. **Apache Superset** - Data visualization dashboards

### Data Flow
```
CSV (23K rows, 7 cols) → Kafka Producer → Kafka Topic (co2-raw)
                              ↓
                        Spark Consumer → PostgreSQL (3 tables)
                              ↓
                        Superset Dashboards
```

**Alternative**: Direct batch load via `batch_processing.py` (CSV → Spark → PostgreSQL)

---

## 📂 Database Schema

### Tables
1. **raw_emissions** (7 columns)
   - All raw data: country, year, iso_code, population, gdp, co2, co2_per_capita
   
2. **country_summary** (aggregated by country)
   - Total CO2, avg per capita, rankings, latest year data
   
3. **yearly_summary** (aggregated by year)
   - Global totals, growth rates, country counts

### Views
- **top_polluters** - Top 10 countries by total CO2
- **top_per_capita** - Top 10 by per capita emissions
- **recent_trends** - Last 20 years of global data

---

## 📁 Project Structure

```
project/
├── README.md                   # This file - Project overview
├── STATUS.md                   # Current deployment status & next steps
├── data/
│   ├── owid-co2-data.csv       # Original dataset (14MB, archived)
│   └── reduced_co2.csv         # 7 columns, 23,405 rows (1900-2014)
├── scripts/
│   └── extract_reduced.py      # Dataset extraction & filtering
├── kafka/
│   ├── producer.py             # Kafka producer (→ co2-raw topic)
│   └── requirements.txt
├── spark/
│   ├── consumer.py             # Kafka → PostgreSQL streaming
│   ├── batch_processing.py     # CSV → PostgreSQL batch load
│   └── requirements.txt
├── sql/
│   └── schema.sql              # 7 columns, 3 tables, 3 views
└── kubernetes/                 # Deployment manifests
    ├── kafka-kraft.yaml
    ├── postgres.yaml
    ├── spark-master.yaml
    ├── spark-worker.yaml
    └── superset.yaml
```

---

## 🚀 Quick Start (Kubernetes/Minikube)

### Prerequisites
- Minikube
- kubectl
- Python 3.8+

### 1. Start Minikube
```bash
minikube start --cpus=2 --memory=4096
```

### 2. Deploy all components
```bash
cd kubernetes
kubectl apply -f kafka-kraft.yaml
kubectl apply -f postgres.yaml
kubectl apply -f spark-master.yaml
kubectl apply -f spark-worker.yaml
kubectl apply -f superset.yaml
```

### 3. Wait for pods to be ready
```bash
kubectl get pods -w
# Wait until all pods show "Running"
```

### 4. Initialize PostgreSQL schema
```bash
kubectl port-forward postgres-0 5432:5432 &
PGPASSWORD=co2_password psql -h localhost -U co2_user -d co2_data -f sql/schema.sql
```

### 5. Create Kafka topic
```bash
kubectl exec -it kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic co2-raw \
  --partitions 3 --replication-factor 1
```

### 6. Load data (Option A: Batch)
```bash
# Get Spark master pod name
SPARK_POD=$(kubectl get pods -l app=spark-master -o jsonpath='{.items[0].metadata.name}')

# Copy CSV file
kubectl cp data/reduced_co2.csv $SPARK_POD:/tmp/

# Run batch processing
kubectl exec -it $SPARK_POD -- spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark-apps/batch_processing.py
```

### 7. Access Superset
```bash
kubectl port-forward svc/superset 8088:8088
# Open http://localhost:8088
# Login: admin/admin
```

**Add PostgreSQL connection in Superset:**
- Host: `postgres.default.svc.cluster.local`
- Port: `5432`
- Database: `co2_data`
- Username: `co2_user`
- Password: `co2_password`

## 📊 Database Schema

### Tables (7 columns matching CSV)
1. **raw_emissions** - All data from Kafka stream
   - country, year, iso_code, population, gdp, co2, co2_per_capita
2. **country_summary** - Aggregated by country (totals, rankings)
3. **yearly_summary** - Aggregated by year (global trends)

### Views
- `top_polluters` - Top 10 countries by total CO2
- `top_per_capita` - Top 10 by per capita emissions
- `recent_trends` - Last 20 years

## 🔧 Useful Commands (Kubernetes)

### Check pod status
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Create Kafka topic
```bash
kubectl exec -it kafka-0 -- kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092
```

### Monitor Kafka messages
```bash
kubectl exec -it kafka-0 -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic co2-raw \
  --from-beginning \
  --max-messages 10
```

### Connect to PostgreSQL
```bash
kubectl port-forward postgres-0 5432:5432
PGPASSWORD=co2_password psql -h localhost -U co2_user -d co2_data
```

### Query data
```sql
-- Count records
SELECT COUNT(*) FROM raw_emissions;

-- Top 10 polluters
SELECT * FROM top_polluters;

-- Recent global trends
SELECT * FROM recent_trends;
```

### Check Spark jobs
```bash
# Port-forward Spark Master UI
kubectl port-forward svc/spark-master 8080:8080
# Open http://localhost:8080
```

## 📈 Superset Dashboards

### Dashboard Ideas
1. **Global Overview**
   - Line chart: Global CO2 over time
   - Area chart: Emission sources (coal, oil, gas)

2. **Country Rankings**
   - Bar chart: Top 10 total polluters
   - Bar chart: Top 10 per capita
   - Table: All countries ranked

3. **Trends Analysis**
   - Scatter: GDP vs CO2
   - Line chart: YoY growth rates
   - Heatmap: Regional emissions

## 🧪 Testing

### Test producer only
```bash
python kafka/producer.py --max-records 100
```

### Test database connection
```bash
docker exec -it postgres psql -U co2_user -d co2_data -c "SELECT COUNT(*) FROM raw_emissions;"
```

### Test Spark locally
```bash
cd spark
pip install -r requirements.txt
python aggregation_job.py
```

## 📝 Development Workflow

1. **Week 1**: Set up Docker Compose environment
2. **Week 2**: Implement and test Kafka producer/consumer
3. **Week 3**: Develop Spark processing jobs
4. **Week 4**: Create Superset dashboards
5. **Week 5**: Deploy to Kubernetes and test

## 🛠️ Troubleshooting

### Kafka not receiving messages
- Check if topic exists: `kubectl exec -it kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092`
- Check producer logs for errors
- Verify port-forward is active: `kubectl port-forward kafka-0 9092:9092`

### Spark consumer not writing to PostgreSQL
- Check PostgreSQL is running: `kubectl get pods | grep postgres`
- Verify JDBC URL uses internal service name: `postgres.default.svc.cluster.local`
- Check Spark logs: `kubectl logs <spark-master-pod>`

### Superset can't connect to PostgreSQL
- Use hostname `postgres.default.svc.cluster.local` (not localhost)
- Verify credentials: co2_user/co2_password
- Check if PostgreSQL pod is running

### Out of memory errors
- Check Minikube resources: `minikube config get memory`
- Reduce Spark worker replicas or memory requests
- Current setup uses 512Mi per Spark pod

### Pod stuck in CrashLoopBackOff
- Check logs: `kubectl logs <pod-name>`
- Describe pod: `kubectl describe pod <pod-name>`
- Verify image versions are correct (apache/kafka:4.1.0, apache/spark:4.0.1)

## 🎯 Success Criteria

- ✅ 23K+ records loaded from reduced CSV
- ✅ Data cleaned and transformed by Spark
- ✅ PostgreSQL contains all 3 tables with data
- ✅ Superset displays interactive dashboards
- ✅ All 5 components running on Kubernetes
- ✅ Pipeline processes data efficiently

## 📚 Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Superset Documentation](https://superset.apache.org/docs/intro)
- [Dataset Source](https://github.com/owid/co2-data)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)

---

## � Implementation Summary

### Completed
✅ Dataset reduced from 79 → 7 columns (1900-2014 filtered)  
✅ Kafka producer for streaming CSV data  
✅ 2 Spark jobs: batch processing + streaming consumer  
✅ PostgreSQL schema (7 columns, 3 tables, 3 views)  
✅ All 5 components deployed to Kubernetes  
✅ Minikube cluster running with all pods active  

### Simplifications Made
- Removed Docker Compose (Kubernetes-only deployment)
- Schema perfectly matches dataset (7 columns everywhere)
- Eliminated duplicate/redundant code (304 lines removed)
- Consolidated to 2 documentation files (README + STATUS)

### Current Phase
� **Week 4**: Database initialization → Data loading → Dashboard creation

### Technical Specs
- **Deployment**: Kubernetes/Minikube (2 CPUs, 4GB RAM)
- **Images**: apache/kafka:4.1.0, apache/spark:4.0.1, postgres:latest
- **Data**: 23,405 rows × 7 columns (1900-2014)
- **Storage**: 12Gi total PVCs (Kafka 5Gi, PostgreSQL 5Gi, Superset 2Gi)

---

## 👥 Project

**IACD** - Data Engineering Pipeline  
**Deployment**: Kubernetes  
**Status**: ✅ Data loaded & analyzed | 🔄 Dashboards ready to create

---

## 📊 Quick Start Guide

### 1️⃣ View Analysis Results
```bash
# See comprehensive findings
cat ANALYSIS.md
```
**Key Findings**:
- ✅ Global CO2 increased 17x from 1900 to 2024
- ✅ COVID caused -4.7% drop (2020) but fully recovered
- ✅ USA leads historically (425K Mt), China leads currently (12.3K Mt)
- ✅ China & India showed explosive growth (+237%, +224% since 2000)

### 2️⃣ Access Superset Dashboards
```bash
# Superset is running and port-forwarded
open http://localhost:8088

# Login: admin / admin
```

**Follow these guides**:
- 📘 **SUPERSET_SETUP.md** - Complete dashboard creation guide (12 charts)
- 📗 **DASHBOARD_QUICK_START.md** - Quick reference for top 10 charts
- 📙 **sql/superset_queries.sql** - 12 categories of ready-to-use queries

### 3️⃣ Query Data Directly
```bash
# PostgreSQL is running and port-forwarded
PGPASSWORD=co2_password psql -h localhost -U co2_user -d co2_data

# Example queries
SELECT * FROM top_polluters LIMIT 10;
SELECT * FROM recent_trends;
SELECT year, total_global_co2 FROM yearly_summary WHERE year >= 2018;
```

### 4️⃣ Optional: Test Kafka Streaming
```bash
# Producer (streams CSV to Kafka)
python kafka/producer.py

# See STATUS.md for Spark consumer commands
```

---

## 📚 Documentation Index

| Document | Purpose | Use When |
|----------|---------|----------|
| **README.md** (this file) | Project overview & architecture | First time setup |
| **STATUS.md** | Current deployment status | Checking what's running |
| **ANALYSIS.md** | Complete data insights | Presenting findings |
| **SUPERSET_SETUP.md** | Full dashboard guide (7 sections) | Creating visualizations |
| **DASHBOARD_QUICK_START.md** | Quick chart reference | Building specific charts |
| **sql/superset_queries.sql** | Pre-built SQL queries | Custom analysis |

---

## 🎯 Current Status

✅ **Infrastructure**: All 5 pods running (Kafka, Spark Master, Spark Worker, PostgreSQL, Superset)  
✅ **Data Loaded**: 23,405 rows (1900-2024, 247 countries, 7 variables)  
✅ **Tables Created**: raw_emissions, country_summary, yearly_summary + 3 views  
✅ **Analysis Complete**: See `ANALYSIS.md` for findings  
✅ **Port-Forwards Active**: PostgreSQL (5432), Superset (8088)  
🔄 **Dashboards**: Ready to create (follow `SUPERSET_SETUP.md`)  

See [`STATUS.md`](STATUS.md) for detailed deployment information.

---

**Last Updated**: November 16, 2025
