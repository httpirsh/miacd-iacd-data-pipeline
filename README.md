# CO2 Data Engineering Pipeline with ML Clustering

A complete data engineering pipeline for analyzing global CO2 emissions with **K-means clustering** using **Kafka, Spark, PostgreSQL, and Superset** deployed on **Kubernetes**.

## Project Overview

### Dataset
**Source:** Our World in Data - CO2 Emissions Dataset
- **Processed**: 31,076 rows (1900-2022), 7 columns, 1.3MB
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

PostgreSQL database `co2_emissions` with tables `co2_clusters` and `cluster_stats`.

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
Minikube, kubectl, Docker, GNU Make

### Quick Start (Recommended)

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=3072

# 2. Run the entire pipeline using Makefile
make run
```

This will build all Docker images, deploy Kubernetes manifests, and set up port forwarding for Superset automatically.

Access Superset at `http://localhost:8088` (admin/admin).

## Spark Consumer Processing

Streaming pipeline that cleans data, aggregates by country, performs K-means clustering, and saves results to PostgreSQL. See [`CONSUMER_LOGIC.md`](CONSUMER_LOGIC.md) for detailed logic.

## ML Clustering

K-means clustering (k=3) with Silhouette Score ~0.84. See [`CONSUMER_LOGIC.md`](CONSUMER_LOGIC.md) for algorithm details.

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
- [STOP_RESUME.md](STOP_RESUME.md) - How to stop and resume the project