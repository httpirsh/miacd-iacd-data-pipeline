.PHONY: all minikube build deploy run producer consumer superset

all: run

minikube:
	@echo "--- Starting Minikube ---"
	minikube start --cpus=4 --memory=8192

build: producer consumer superset

producer: .make/producer

consumer: .make/consumer

superset: .make/superset

.make:
	mkdir -p .make

.make/producer: .make kafka/*
	@echo "--- Building Kafka Producer Docker Image ---"
	@eval $$(minikube docker-env); docker build -t kafka-producer:latest -f kafka/Dockerfile .
	@touch .make/producer

.make/consumer: .make spark/*
	@echo "--- Building Spark Consumer Docker Image ---"
	@eval $$(minikube docker-env); docker build -t spark-consumer:latest -f spark/Dockerfile spark/
	@touch .make/consumer

.make/superset: superset/*
	@echo "--- Building Superset Docker Image ---"
	@eval $$(minikube docker-env); docker build -t superset:latest -f superset/Dockerfile superset/
	@touch .make/superset

deploy: build
	@echo "--- Deploying Kubernetes Manifests ---"
	kubectl apply -f kubernetes/

run: deploy
	@echo "--- Accessing Superset (Port Forwarding) ---"
	@echo "Access Superset at http://localhost:8088 (admin/admin)"
	kubectl port-forward service/superset 8088:8088

# Whenever you do minikube delete, also do rm -rf .make!​