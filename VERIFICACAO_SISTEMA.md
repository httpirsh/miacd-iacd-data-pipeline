# ✅ Status do Sistema - Verificação Local

## Data: 2025-11-26

### 🔍 Verificação Realizada

**Problema Identificado:** Consumer estava a crashar com erro `'str' object has no attribute 'alias'`

**Causa:** Faltavam imports `min` e `max` do `pyspark.sql.functions`

**Solução:** 
```python
# Antes
from pyspark.sql.functions import from_json, col, avg, count as count_func, ...

# Depois
from pyspark.sql.functions import from_json, col, avg, count as count_func, ..., min, max
```

---

## 📊 Estado Atual do Cluster

### Pods em Execução:
```
✅ kafka-0                    - Running (163m)
✅ kafka-producer             - Running (164m)  
✅ postgres                   - Running (135m)
✅ spark-consumer (antigo)    - Running (51m) ← Versão com bug
✅ spark-master               - Running (164m)
✅ spark-worker               - Running (164m)
✅ superset                   - Running (11m)
```

### Dados no PostgreSQL:
```sql
SELECT COUNT(*) FROM co2_clusters;
-- 6055 registos ✅
```

---

## ⚠️ Problema Atual: ImagePullBackOff

**O que aconteceu:**
1. Removemos `imagePullPolicy: Never` dos manifestos
2. Kubernetes tentou criar novos pods
3. Tentou fazer `pull` das imagens do DockerHub
4. Falhou porque imagens são locais, não estão no DockerHub

**Sintoma:**
```
kafka-producer-78c475789-xxx    0/1  ErrImagePull
spark-consumer-5bb67c999b-xxx   0/1  ErrImagePull   
```

---

## 🔧 2 Opções para Resolver

### **Opção A: Reverter imagePullPolicy** (Rápido) ⭐

Adicionar de volta `imagePullPolicy: IfNotPresent` nos manifestos:

```yaml
# 05-kafka-producer.yaml
containers:
- name: producer
  image: kafka-producer:latest
  imagePullPolicy: IfNotPresent  # ← Adicionar

# 06-spark-consumer.yaml
containers:
- name: consumer
  image: spark-consumer:latest
  imagePullPolicy: IfNotPresent  # ← Adicionar

# 07-superset.yaml
containers:
- name: superset
  image: superset-postgres:v2
  imagePullPolicy: IfNotPresent  # ← Adicionar
```

**Vantagem:**
- ✅ Funciona imediatamente
- ✅ Usa imagens locais
- ✅ Não precisa DockerHub

---

### **Opção B: Push para DockerHub** (Profissional)

1. Fazer push das imagens para DockerHub
2. Atualizar manifestos com username
3. Kubernetes faz pull automático

**Passos:**
```bash
# Build com username
docker build -t catarinafelixcr/kafka-producer:latest ./kafka
docker build -t catarinafelixcr/spark-consumer:latest ./spark
docker build -t catarinafelixcr/superset-postgres:v2 ./superset

# Push para DockerHub (precisa login)
docker login
docker push catarinafelixcr/kafka-producer:latest
docker push catarinafelixcr/spark-consumer:latest
docker push catarinafelixcr/superset-postgres:v2
```

**Vantagem:**
- ✅ Professor pode correr diretamente
- ✅ Workflow profissional
- ✅ Funciona em qualquer cluster

---

## 📋 Checklist de Verificação

### Infraestrutura:
- [x] PostgreSQL - Running ✅
- [x] Kafka - Running ✅
- [x] Spark Master/Worker - Running ✅
- [x] Superset - Running ✅

### Aplicações:
- [x] Kafka Producer - Running ✅
- [⚠️] Spark Consumer - Running (versão antiga com bug corrigido, precisa restart)

### Dados:
- [x] PostgreSQL tem 6055 registos ✅
- [x] Producer está a enviar dados ✅
- [⚠️] Consumer está a crashar (bug corrigido, precisa nova versão)

### Problemas:
- [ ] Novos pods com ImagePullBackOff 
- [ ] Consumer com bug (versão antiga ainda a correr)

---

## ✅ Próximos Passos Recomendados

1. **DECIDIR:** Opção A (IfNotPresent) ou Opção B (DockerHub)?

2. **Se Opção A:**
   - Adicionar `imagePullPolicy: IfNotPresent` nos 3 manifestos
   - `kubectl apply -f kubernetes/`
   - Verificar pods ficam Running

3. **Se Opção B:**
   - Push das 3 imagens para DockerHub
   - Atualizar manifestos com `catarinafelixcr/...`
   - `kubectl apply -f kubernetes/`

4. **Testar:** 
   - Ver logs do consumer (deve mostrar clustering a funcionar)
   - Verificar dados no PostgreSQL
   - Aceder Superset

---

## 💡 Minha Recomendação

**Para AGORA (desenvolvimento):**
→ **Opção A** `imagePullPolicy: IfNotPresent`
- Rápido, funciona logo
- Desenvolvimento local eficiente

**Para ENTREGA (professor avaliar):**
→ **Opção B** DockerHub
- Professor corre sem rebuild
- Mais profissional
- Workflow real

**Podes fazer Opção A agora e Opção B depois!** 😊
