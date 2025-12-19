# Guide: Stop and Resume the Project Safely 🛑▶️

This guide explains how to shut down everything without losing your data (Superset dashboards, database, etc.) and how to restart when you want to work again.

---

## 🛑 How to Stop (Safe Shutdown)

### 1. Stop Port-Forwards
In terminals where you have `kubectl port-forward` commands running:
- Press **Ctrl + C** to stop the process
- You can close those terminal windows

### 2. Stop Minikube
This command "freezes" the Kubernetes cluster and saves all state (including disks/volumes).
```bash
minikube stop
```
*Note: Don't use `minikube delete`, as that erases everything!*

### 3. (Optional) Shut Down Computer
Now you can safely shut down your computer. Data is saved in Minikube's disk.

---

## ▶️ How to Resume (Return to Work)

When you want to return to the project:

### 1. Start Minikube
```bash
minikube start
```
*Wait a few minutes until all pods are running.*

### 2. Check Status
```bash
kubectl get pods
```
*Wait until you see `Running` on all (Superset, Postgres, Spark, Kafka).*

### 3. Reactivate Port-Forwards

**Why do you need this?**  
Services (Superset, PostgreSQL, Spark) use `ClusterIP`, which means they're only accessible **inside** the Kubernetes cluster. To access from outside (your browser or computer), you need to create "tunnels" with `kubectl port-forward`.

#### ✅ **REQUIRED - Superset Port-Forward**

This is the **ONLY** port-forward you **always** need:

**Terminal 1 (keep this terminal open!):**
```bash
kubectl port-forward svc/superset 8088:8088
```

Then open browser: `http://localhost:8088` (admin / admin)

**Note:** While this terminal is open, Superset works. If you close the terminal, Superset becomes inaccessible (but continues running in the cluster).

---

#### ⚠️ **OPTIONAL - Other Port-Forwards**

**You only need these IF you want to:**

**PostgreSQL (Terminal 2 - OPTIONAL):**
```bash
kubectl port-forward svc/postgres 5432:5432
```
**When to use:** If you want to access PostgreSQL with DBeaver, pgAdmin or `psql` to view data directly.  
**Not needed if:** You only use Superset (Superset already accesses PostgreSQL internally).

**Spark Master UI (Terminal 3 - OPTIONAL):**
```bash
kubectl port-forward svc/spark-master 8080:8080
```
**When to use:** If you want to see Spark statistics (connected workers, memory usage, jobs).  
**Not needed if:** You just want the pipeline to work (not necessary for the project).

---

### 4. Access Services

**What you can access (with active port-forwards):**

| Service | URL | Credentials | Port-Forward Required? |
|---------|-----|-------------|------------------------|
| **Superset** | `http://localhost:8088` | admin / admin | ✅ **YES (required)** |
| PostgreSQL | `localhost:5432` | postgres / postgres | ⚠️ Only if you want access |
| Spark UI | `http://localhost:8080` | - | ⚠️ Only for curiosity |

---

### 5. What's Saved vs. What's Lost

**✅ Data that persists after `minikube stop`:**
- Superset dashboards (saved in persistent volume)
- All PostgreSQL data (tables, records)
- Superset configurations and datasets
- Kafka data (StatefulSet volume)

**❌ What's lost:**
- Messages still in transit in Kafka (not persisted)
- Spark jobs mid-execution (will restart)
- Port-forwards (you need to reopen when you return)

**Conclusion:** When you run `minikube start` after `minikube stop`, **everything returns exactly as it was!** You just need to reopen the Superset port-forward.

---

## ⚠️ What to NEVER do if you want to keep data
- ❌ **NEVER run `minikube delete`** (deletes the entire cluster)
- ❌ **NEVER run `kubectl delete pvc --all`** (deletes persistent disks)