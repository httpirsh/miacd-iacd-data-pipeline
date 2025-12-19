# Stop and Resume the Project

## Stop

1. In terminals with `port-forward`, press **Ctrl+C** to stop
2. Run:
   ```bash
   minikube stop
   ```

**Note:** Never use `minikube delete` - it erases everything!

---

## Resume (Step-by-Step)

### Step 1: Start Minikube
```bash
minikube start
```

### Step 2: Verify pods are running
```bash
kubectl get pods
```
Wait until all pods show `STATUS: Running` (30-60 seconds).

### Step 3: Run the pipeline
```bash
make run
```
This will open the Superset port-forward automatically.

### Step 4: View logs (in another terminal)

```bash
# Spark Consumer (data processing) - MOST IMPORTANT
kubectl logs deployment/spark-consumer --tail=50

# Kafka Producer (data sending)
kubectl logs job/kafka-producer --tail=30

# Kafka Broker
kubectl logs kafka-0 --tail=30

# PostgreSQL
kubectl logs deployment/postgres --tail=30

# Superset
kubectl logs deployment/superset --tail=30
```

**Follow logs in real-time** (add `-f`):
```bash
kubectl logs deployment/spark-consumer -f
```

### Step 5: Access Superset

Open: http://localhost:8088
- **Username:** admin
- **Password:** admin

---

## Optional port-forwards

Only needed if you want direct access:

```bash
# PostgreSQL (for pgAdmin)
kubectl port-forward svc/postgres 5432:5432

# Spark UI (to see stats)
kubectl port-forward svc/spark-master 8080:8080
```

---

## What is saved

- Superset dashboards
- PostgreSQL data
- Kafka data

## What is lost

- Kafka messages in transit
- Spark jobs mid-execution
- Port-forwards (need to reopen)
