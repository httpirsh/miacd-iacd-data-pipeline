# Guia: Parar e Retomar o Projeto em Segurança 🛑▶️

Este guia explica como desligar tudo sem perder os teus dados (Dashboards do Superset, Base de Dados, etc.) e como voltar a ligar quando quiseres trabalhar novamente.

---

## 🛑 Como Parar (Encerramento Seguro)

### 1. Parar os Port-Forwards
Nos terminais onde tens os comandos `kubectl port-forward` a correr:
- Clica **Ctrl + C** para parar o processo.
- Podes fechar essas janelas de terminal.

### 2. Parar o Minikube
Este comando "congela" o cluster Kubernetes e guarda todo o estado (incluindo discos/volumes).
```bash
minikube stop
```
*Nota: Não uses `minikube delete`, pois isso apaga tudo!*

### 3. (Opcional) Desligar o Computador
Agora podes desligar o computador à vontade. Os dados estão salvos no disco do Minikube.

---

## ▶️ Como Retomar (Voltar a Trabalhar)

Quando quiseres voltar ao projeto:

### 1. Iniciar o Minikube
```bash
minikube start
```
*Aguarda uns minutos até todos os "pods" estarem a correr.*

### 2. Verificar Estado
```bash
kubectl get pods
```
*Espera até veres `Running` em todos (Superset, Postgres, Spark, Kafka).*

### 3. Reativar Port-Forwards (Essencial!)
Abre terminais novos e corre:

**Terminal 1 (Superset):**
```bash
kubectl port-forward svc/superset 8088:8088
```

**Terminal 2 (PostgreSQL - Opcional):**
```bash
kubectl port-forward svc/postgres 5432:5432
```

### 4. Aceder
- Superset: `http://localhost:8088`
- Tudo estará exatamente como deixaste! 🎉

---

## ⚠️ O que NUNCA fazer se quiseres manter dados
- ❌ **NUNCA corras `minikube delete`** (apaga o cluster todo)
- ❌ **NUNCA corras `kubectl delete pvc --all`** (apaga os discos persistentes)
