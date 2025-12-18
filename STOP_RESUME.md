# Stop and Resume the Project

## Stop

1. In terminals with `port-forward`, press **Ctrl+C** to stop
2. Run:
   ```bash
   minikube stop
   ```

**Note:** Never use `minikube delete` - it erases everything!

## Resume

1. Start minikube:
   ```bash
   minikube start
   ```

2. Wait for pods to start:
   ```bash
   kubectl get pods
   ```

3. Open the Superset port-forward:
   ```bash
   kubectl port-forward svc/superset 8088:8088
   ```

4. Access Superset: http://localhost:8088 (admin / admin)

### Optional port-forwards

Only needed if you want direct access:

```bash
# PostgreSQL (for pgAdmin)
kubectl port-forward svc/postgres 5432:5432

# Spark UI (to see stats)
kubectl port-forward svc/spark-master 8080:8080
```

## What is saved

- Superset dashboards
- PostgreSQL data
- Kafka data

## What is lost

- Kafka messages in transit
- Spark jobs mid-execution
- Port-forwards (need to reopen)
