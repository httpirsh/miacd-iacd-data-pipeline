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

### 3. Reativar Port-Forwards

**Porque precisas disto?**  
Os serviços (Superset, PostgreSQL, Spark) usam `ClusterIP`, o que significa que só são acessíveis **dentro** do cluster Kubernetes. Para acederes de fora (do teu browser ou computador), precisas de criar "túneis" com `kubectl port-forward`.

#### ✅ **OBRIGATÓRIO - Port-Forward do Superset**

Este é o **ÚNICO** port-forward que precisas **sempre**:

**Terminal 1 (deixa este terminal aberto!):**
```bash
kubectl port-forward svc/superset 8088:8088
```

Depois abre browser: `http://localhost:8088` (admin / admin)

**Nota:** Enquanto este terminal estiver aberto, o Superset funciona. Se fechares o terminal, o Superset fica inacessível (mas continua a correr no cluster).

---

#### ⚠️ **OPCIONAL - Outros Port-Forwards**

**Só precisas destes SE quiseres:**

**PostgreSQL (Terminal 2 - OPCIONAL):**
```bash
kubectl port-forward svc/postgres 5432:5432
```
**Quando usar:** Se quiseres aceder ao PostgreSQL com DBeaver, pgAdmin ou `psql` para ver os dados diretamente.  
**Não precisas se:** Só usas o Superset (o Superset já acede ao PostgreSQL internamente).

**Spark Master UI (Terminal 3 - OPCIONAL):**
```bash
kubectl port-forward svc/spark-master 8080:8080
```
**Quando usar:** Se quiseres ver estatísticas do Spark (workers conectados, memória usada, jobs).  
**Não precisas se:** Só queres que o pipeline funcione (não é necessário para o projeto).

---

### 4. Aceder aos Serviços

**O que podes aceder (com port-forwards ativos):**

| Serviço | URL | Credenciais | Port-Forward Necessário? |
|---------|-----|-------------|--------------------------|
| **Superset** | `http://localhost:8088` | admin / admin | ✅ **SIM (obrigatório)** |
| PostgreSQL | `localhost:5432` | postgres / postgres | ⚠️ Só se quiseres aceder |
| Spark UI | `http://localhost:8080` | - | ⚠️ Só por curiosidade |

---

### 5. O Que Fica Guardado vs. O Que Se Perde

**✅ Dados que persistem após `minikube stop`:**
- Dashboards do Superset (guardados no volume persistente)
- Todos os dados do PostgreSQL (tabelas, registos)
- Configurações e datasets do Superset
- Dados do Kafka (volume do StatefulSet)

**❌ O que se perde:**
- Mensagens ainda em trânsito no Kafka (não persistidas)
- Jobs Spark a meio da execução (vão recomeçar)
- Port-forwards (tens de reabrir quando voltares)

**Conclusão:** Quando fazes `minikube start` após um `minikube stop`, **tudo volta exatamente como estava!** Só tens de reabrir o port-forward do Superset.

---

## ⚠️ O que NUNCA fazer se quiseres manter dados
- ❌ **NUNCA corras `minikube delete`** (apaga o cluster todo)
- ❌ **NUNCA corras `kubectl delete pvc --all`** (apaga os discos persistentes)
