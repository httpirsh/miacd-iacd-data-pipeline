# CO2 Data Engineering Pipeline with ML Clustering

A complete data engineering pipeline for analyzing global CO2 emissions with **K-means clustering** using **Kafka, Spark, PostgreSQL, and Superset** deployed on **Kubernetes**.

## Project Overview

### Dataset
**Source:** Our World in Data - CO2 Emissions Dataset
- **Processed**: 23,405 rows (1900-2024), 7 columns, 1.4MB
- **Variables**: country, year, iso_code, population, gdp, co2, co2_per_capita

## Architecture

### Components
1. **Apache Kafka (KRaft mode)** - Message broker
2. **Apache Spark (Local Mode)** - K-means clustering (k=3)
3. **PostgreSQL** - Storage
4. **Apache Superset** - Visualization

### Data Flow
```
CSV → Kafka Producer → Spark Consumer (K-means) → PostgreSQL → Superset
```

## Database Schema

PostgreSQL database `co2_emissions` with tables `co2_clusters` and `cluster_stats`. See [`SUPERSET_SETUP.md`](SUPERSET_SETUP.md) for schema details.

## Project Structure

```
project/
├── data/              # CSV datasets (original + reduced)
├── scripts/           # EDA and extraction scripts
├── kafka/             # Producer Dockerfile + code
├── spark/             # Consumer Dockerfile + code
├── postgres/          # Database init schema
├── superset/          # Custom Superset Dockerfile
└── kubernetes/        # K8s manifests (01-05.yaml)
```

## Usage

### Prerequisites
Minikube, kubectl, Docker

### Deployment Steps

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Build images in Minikube
eval $(minikube docker-env)
docker build -t kafka-producer:latest -f kafka/Dockerfile .
docker build -t spark-consumer:latest -f spark/Dockerfile spark/
docker build -t superset:latest -f superset/Dockerfile superset/

# 3. Deploy
kubectl apply -f kubernetes/

# 4. Verify
kubectl get pods
kubectl logs job/kafka-producer --tail=20
kubectl logs -l app=spark-consumer --tail=50
```

### Accessing Services

```bash
kubectl port-forward service/superset 8088:8088
```

Access Superset at `http://localhost:8088` (admin/admin).

## Spark Consumer Processing

Streaming pipeline that cleans data, aggregates by country, performs K-means clustering, and saves results to PostgreSQL. See [`CONSUMER_LOGIC.md`](CONSUMER_LOGIC.md) for detailed logic.

## ML Clustering

K-means clustering (k=3) with Silhouette Score ~0.96. See [`CONSUMER_LOGIC.md`](CONSUMER_LOGIC.md) for algorithm details.

## Useful Commands

```bash
# Access PostgreSQL
kubectl exec -it deployment/postgres -- psql -U postgres -d co2_emissions

# Restart components
kubectl rollout restart deployment/spark-consumer
kubectl rollout restart deployment/superset
```

## Troubleshooting

```bash
# ImagePullBackOff: rebuild images
eval $(minikube docker-env)
docker build -t kafka-producer:latest -f kafka/Dockerfile .

# Check logs
kubectl logs deployment/superset
kubectl logs deployment/spark-consumer --tail=50
```

## Technology Stack

Kafka 4.1.0 (KRaft) • Spark 4.0.1 • PostgreSQL 15 • Superset • Kubernetes • Python 3.11

## Additional Documentation

- [CONSUMER_LOGIC.md](CONSUMER_LOGIC.md) - Consumer logic details
- [SUPERSET_SETUP.md](SUPERSET_SETUP.md) - Dashboard setup
- [STOP_RESUME.md](STOP_RESUME.md) - How to stop and resume the project
