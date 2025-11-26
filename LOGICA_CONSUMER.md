# 🔍 Lógica do Spark Consumer - Explicação Detalhada

## Fluxo Geral (Visão Macro)

```
Kafka (mensagens JSON) 
    ↓
Spark Consumer lê em batches (15 segundos)
    ↓
Limpa dados (remove NaNs, agregados)
    ↓
Agrupa por país (média de CO2, GDP, etc)
    ↓
K-means Clustering (3 clusters)
    ↓
Guarda em PostgreSQL (co2_clusters, cluster_stats)
```

---

## Passo-a-Passo Detalhado

### 1️⃣ **Conexão ao Kafka** (linhas 226-262)

```python
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "emissions-topic") \
    .option("startingOffsets", "earliest") \
    .load()
```

**O que faz:**
- Conecta ao Kafka (broker em `kafka:9092`)
- Subscreve tópico `emissions-topic`
- Lê mensagens desde o início (`earliest`)

**Output:** Stream contínuo de mensagens

---

### 2️⃣ **Parse JSON** (linhas 243-247)

```python
json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")
processed_stream_df = json_df.select(
    from_json(col("json_string"), schema).alias("data")
).select("data.*")
```

**O que faz:**
- Converte bytes Kafka → String
- Faz parse do JSON usando schema definido
- Extrai campos: country, year, iso_code, population, gdp, co2, co2_per_capita

**Exemplo de mensagem:**
```json
{
  "country": "Portugal",
  "year": 2020,
  "iso_code": "PRT",
  "population": 10196709,
  "gdp": 231049256960,
  "co2": 45.89,
  "co2_per_capita": 4.5
}
```

---

### 3️⃣ **Limpeza de Dados** (linhas 59-87)

```python
# Converte "NaN" string → NULL
for col_name in ["gdp", "population", "co2", "co2_per_capita"]:
    all_data = all_data.withColumn(
        col_name,
        when((col(col_name) == "NaN"), None).otherwise(col(col_name))
    )

# Filtra agregados (World, Europe, etc)
all_data = all_data.filter(
    (col("iso_code").isNotNull()) & 
    (col("iso_code") != "NaN")
)
```

**O que faz:**
- String "NaN" (do Pandas) → NULL (do Spark)
- Remove registos onde `iso_code` é NULL (agregados como "World", "Africa")

**Porquê?** 
- "World" não é um país, é soma de todos
- Queremos só países individuais

---

### 4️⃣ **Agregação por País** (linhas 93-100)

```python
country_stats = all_data.groupBy("country", "iso_code").agg(
    avg("co2").alias("avg_co2"),
    avg("co2_per_capita").alias("avg_co2_per_capita"),
    avg("gdp").alias("avg_gdp"),
    avg("population").alias("avg_population"),
    count("*").alias("data_points")
).filter((col("avg_co2").isNotNull()) & (col("data_points") >= 5))
```

**O que faz:**
- Agrupa dados por **país**
- Calcula **médias** de todas as variáveis (CO2, GDP, população)
- Conta quantos registos (anos) cada país tem
- Só mantém países com ≥5 anos de dados

**Exemplo de resultado:**
```
Country    | avg_co2 | avg_gdp       | avg_population
-----------|---------|---------------|---------------
Portugal   | 52.3    | 220000000000  | 10200000
Germany    | 850.2   | 3800000000000 | 83000000
```

---

### 5️⃣ **Preparação para Clustering** (linhas 116-126)

```python
feature_cols = ["avg_co2", "avg_co2_per_capita", "avg_gdp", "avg_population"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

cleaned_data = country_stats.na.drop()  # Remove NULLs

scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
```

**O que faz:**
- **VectorAssembler:** Junta as 4 colunas num vetor único
  - `[52.3, 4.5, 220000000000, 10200000]` → vetor
- **StandardScaler:** Normaliza valores (0-1)
  - Porquê? GDP é muito maior que CO2, sem escalar o clustering ignora variáveis pequenas

**Antes:**
```
avg_gdp: 220000000000 (ENORME)
avg_co2: 52.3 (pequeno)
```

**Depois (scaled):**
```
gdp_scaled: 0.35
co2_scaled: 0.42
```

---

### 6️⃣ **K-means Clustering** (linhas 128-143)

```python
k = 3  # 3 clusters
kmeans = KMeans(
    k=k, 
    featuresCol="scaled_features", 
    predictionCol="cluster",
    seed=42,
    maxIter=20
)

pipeline = Pipeline(stages=[assembler, scaler, kmeans])
model = pipeline.fit(cleaned_data)
results = model.transform(cleaned_data)
```

**O que faz:**
- **K-means:** Algoritmo de clustering (agrupa dados similares)
- **k=3:** Cria 3 grupos de países
- **seed=42:** Garante resultados reproduzíveis
- **Pipeline:** Executa assembler → scaler → kmeans em sequência

**Resultado:** Cada país recebe um `cluster` (0, 1 ou 2)

**Exemplo:**
```
Country    | avg_co2 | avg_gdp | cluster
-----------|---------|---------|--------
Portugal   | 52.3    | 2.2e11  | 1
USA        | 5000.0  | 2.1e13  | 2
Chad       | 2.5     | 1.1e10  | 0
```

**Interpretação dos Clusters:**
- **Cluster 0:** Baixo CO2, baixo GDP (países em desenvolvimento)
- **Cluster 1:** Médio CO2, médio GDP (países desenvolvidos médios)
- **Cluster 2:** Alto CO2, alto GDP (países grandes/industrializados)

---

### 7️⃣ **Guardar em PostgreSQL** (linhas 146-173)

```python
# Preparar dados
results_for_db = results.select(
    "country", "iso_code", "avg_co2", "avg_co2_per_capita", 
    "avg_gdp", "avg_population", "cluster"
).withColumn("batch_id", lit(batch_id))

# Guardar tabela principal
save_to_postgresql(results_for_db, batch_id, "co2_clusters")

# Estatísticas por cluster
cluster_stats = results.groupBy("cluster").agg(
    count("*").alias("num_countries"),
    avg("avg_co2").alias("avg_co2_cluster"),
    ...
)
save_to_postgresql(cluster_stats, batch_id, "cluster_stats")
```

**O que faz:**
- Seleciona colunas relevantes
- Adiciona `batch_id` (identificador do processamento)
- Guarda em 2 tabelas:
  1. **`co2_clusters`:** Cada país com seu cluster
  2. **`cluster_stats`:** Médias por cluster

---

### 8️⃣ **Clustering Temporal** (linhas 175-217) ⚠️

**NOTA:** Esta parte dissemos que é **desnecessária** e pode ser removida para simplificar!

Faz clustering por país **E** ano (mais complexo, não recomendado).

---

## 🔄 Loop Contínuo (linha 272-277)

```python
query = kafka_stream.writeStream \
    .outputMode("update") \
    .foreachBatch(process_clustering) \
    .trigger(processingTime="15 seconds") \
    .start()
```

**O que faz:**
- A cada **15 segundos**, chama `process_clustering()`
- Processa batch de mensagens acumuladas
- Loop infinito (até Ctrl+C)

---

## 📊 Resumo Visual Completo

```
┌─────────────────────────────────────────────────────────┐
│ KAFKA (mensagens JSON de países)                       │
└─────────────────────┬───────────────────────────────────┘
                      │ Streaming (15s batches)
                      ↓
┌─────────────────────────────────────────────────────────┐
│ SPARK CONSUMER                                          │
│                                                         │
│  1. Parse JSON         → DataFrame                     │
│  2. Limpa NaNs         → Remove agregados              │
│  3. Agrupa por país    → Médias (CO2, GDP, pop)        │
│  4. Normaliza          → StandardScaler                │
│  5. K-means (k=3)      → Atribui clusters 0/1/2        │
│  6. Guarda PostgreSQL  → co2_clusters, cluster_stats   │
│                                                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│ POSTGRESQL                                              │
│  ├─ co2_clusters (país + cluster)                      │
│  └─ cluster_stats (médias por cluster)                 │
└─────────────────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│ SUPERSET (lê e visualiza)                              │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Conceitos Chave para Explicar

### **1. Streaming**
Em vez de processar tudo de uma vez, processa **continuamente** a cada 15s.

### **2. K-means**
Algoritmo que agrupa dados similares automaticamente (sem supervisão).

### **3. StandardScaler**
Normaliza valores para todas as variáveis terem o mesmo "peso" no clustering.

### **4. Pipeline**
Sequência de transformações (assembler → scaler → kmeans) executadas automaticamente.

---

**Esta é a lógica completa do Consumer!** Está mais claro agora? 😊
