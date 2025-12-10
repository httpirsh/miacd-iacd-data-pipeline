# Project Overview

This project is a complete data engineering pipeline for analyzing global CO2 emissions. It uses a variety of tools to create a stream processing system that cleans data, performs machine learning clustering, and stores the results for visualization.

The core technologies used are:

*   **Apache Kafka:** Acts as a message broker, streaming CO2 data from a producer to a consumer.
*   **Apache Spark:** The consumer, which processes the data in real-time. It cleans the data, aggregates it by country, and then applies a K-means clustering algorithm to group countries with similar emission profiles.
*   **PostgreSQL:** A relational database used to store the results of the Spark processing, including the cluster assignments for each country and overall cluster statistics.
*   **Apache Superset:** A data visualization platform used to create dashboards and explore the results stored in PostgreSQL.
*   **Kubernetes:** The entire application is containerized and deployed on a Kubernetes cluster, allowing for scalable and resilient operation.
*   **Python:** The language used for the Kafka producer and the Spark consumer.

## Building and Running the Project

The project is designed to be run in a local Kubernetes cluster using Minikube.

### Prerequisites

*   Minikube
*   kubectl
*   Docker

### Deployment Steps

1.  **Start Minikube:**
    ```bash
    minikube start --cpus=4 --memory=3072 --force
    ```

2.  **Build Docker Images:**
    The project uses several custom Docker images. These must be built within Minikube's Docker environment.
    ```bash
    eval $(minikube docker-env)
    docker build -t kafka-producer:latest -f kafka/Dockerfile .
    docker build -t spark-consumer:latest -f spark/Dockerfile spark/
    docker build -t superset:latest -f superset/Dockerfile superset/
    ```

3.  **Deploy Kubernetes Manifests:**
    The Kubernetes manifests in the `kubernetes/` directory define all the necessary components for the application.
    ```bash
    kubectl apply -f kubernetes/
    ```

4.  **Accessing Services:**
    To access the Superset web interface, you need to forward the service port:
    ```bash
    kubectl port-forward service/superset 8088:8088
    ```
    You can then access Superset at `http://localhost:8088` with the credentials `admin`/`admin`.

### Stopping and Resuming

*   **To stop the application:** `minikube stop`
*   **To resume the application:** `minikube start` and then re-apply the port forward for Superset.

## Development Conventions

*   The application is divided into several components, each in its own directory (`kafka`, `spark`, `postgres`, `superset`).
*   Each component has its own Dockerfile for containerization.
*   Kubernetes is used for orchestration, with YAML manifests defining the desired state of the application.
*   The Spark consumer logic is well-documented in `CONSUMER_LOGIC.md`, which explains each step of the data processing pipeline.
*   Python code uses type hints and clear function definitions.
*   The database schema is defined in `postgres/init.sql`, which is automatically executed when the PostgreSQL container starts.
*   The `requirements.txt` file lists all the Python dependencies for the project.
