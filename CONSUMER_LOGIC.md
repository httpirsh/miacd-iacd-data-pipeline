# 🔍 Spark Consumer Logic - Detailed Explanation

## General Flow (Macro View)

```
Kafka (JSON messages) 
    ↓
Spark Consumer reads in batches (15 seconds)
    ↓
Clean data (remove NaNs, aggregates)
    ↓
Group by country (average CO2, GDP, etc)
    ↓
K-means Clustering (3 clusters)
    ↓
Save to PostgreSQL (co2_clusters, cluster_stats)
```

---

## Step-by-Step Details

### 1️⃣ **Kafka Connection** (lines 226-262)

```python
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "emissions-topic") \
    .option("startingOffsets", "earliest") \
    .load()
```

**What it does:**
- Connects to Kafka (broker at `kafka:9092`)
- Subscribes to `emissions-topic`
- Reads messages from the beginning (`earliest`)

**Output:** Continuous message stream

---

### 2️⃣ **JSON Parsing** (lines 243-247)

```python
json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")
processed_stream_df = json_df.select(
    from_json(col("json_string"), schema).alias("data")
).select("data.*")
```

**What it does:**
- Converts Kafka bytes → String
- Parses JSON using defined schema
- Extracts fields: country, year, iso_code, population, gdp, co2, co2_per_capita

**Example message:**
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

### 3️⃣ **Data Cleaning** (lines 59-87)

```python
# Convert "NaN" string → NULL
for col_name in ["gdp", "population", "co2", "co2_per_capita"]:
    all_data = all_data.withColumn(
        col_name,
        when((col(col_name) == "NaN"), None).otherwise(col(col_name))
    )

# Filter aggregates (World, Europe, etc)
all_data = all_data.filter(
    (col("iso_code").isNotNull()) & 
    (col("iso_code") != "NaN")
)
```

**What it does:**
- String "NaN" (from Pandas) → NULL (in Spark)
- Removes records where `iso_code` is NULL (aggregates like "World", "Africa")

**Why?** 
- "World" is not a country, it's a sum of all
- We want only individual countries

---

### 4️⃣ **Country Aggregation** (lines 93-100)


```python
country_stats = all_data.groupBy("country", "iso_code").agg(
    avg("co2").alias("avg_co2"),
    avg("co2_per_capita").alias("avg_co2_per_capita"),
    avg("gdp").alias("avg_gdp"),
    avg("population").alias("avg_population"),
    count("*").alias("data_points"),
    min("year").alias("first_year"),
    max("year").alias("last_year"),
    avg(when(col("year") >= 2010, col("co2")).alias("avg_co2_recent"))
)
# Log excluded countries for debugging
excluded = all_data.groupBy("country", "iso_code").agg(
    count("*").alias("data_points")
).filter(col("data_points") < 1)
excluded_countries = [row['country'] for row in excluded.collect()]
if excluded_countries:
    print(f"Excluded countries (less than 1 year of data): {excluded_countries}")
country_stats = country_stats.filter(
    (col("avg_co2").isNotNull()) & 
    (col("avg_co2_per_capita").isNotNull()) & 
    (col("data_points") >= 1)
)
```

**What it does:**
- Groups data by **country**
- Calculates **averages** of all variables (CO2, GDP, population)
- Counts how many records (years) each country has
- Keeps only countries with ≥1 year of data (previously 5)
- Logs excluded countries for debugging

**Example result:**
```
Country    | avg_co2 | avg_gdp       | avg_population | data_points
-----------|---------|---------------|---------------|------------
Portugal   | 52.3    | 220000000000  | 10200000      | 10
Chad       | 2.5     | 11000000000   | 15000000      | 1
```

---


### 5️⃣ **Clustering Preparation** (lines 116-126)

```python
# Features for clustering (GDP excluded for better separation)
feature_cols = ["avg_co2", "avg_co2_per_capita", "avg_population"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
cleaned_data = country_stats.na.drop()  # Remove NULLs
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
```

**What it does:**
- **VectorAssembler:** Combines selected columns into a single vector
- **StandardScaler:** Normalizes values so all features contribute equally

**Note:** GDP is excluded from clustering to improve separation between emission groups.

---


### 6️⃣ **Hybrid Clustering & Relabeling** (lines 128-143)

```python
k = 3  # 3 clusters
kmeans = KMeans(
    k=k,
    featuresCol="scaled_features",
    predictionCol="cluster_original",
    seed=42,
    maxIter=100
)
pipeline = Pipeline(stages=[assembler, scaler, kmeans])
model = pipeline.fit(cleaned_data)
results = model.transform(cleaned_data)

# Relabel clusters by average CO2
cluster_avg_co2 = results.groupBy("cluster_original").agg(avg("avg_co2").alias("avg_co2_in_cluster")).collect()
cluster_mapping = sorted(
    [(row["cluster_original"], row["avg_co2_in_cluster"]) for row in cluster_avg_co2],
    key=lambda x: x[1]
)
relabel_map = {cluster_mapping[i][0]: i for i in range(len(cluster_mapping))}
# Apply relabeling
# ... (see code for details)
results = results.withColumn("cluster", mapping_expr)
```

**What it does:**
- Performs K-means clustering (k=3) on scaled features
- Relabels clusters by average CO2: 0 = Low, 1 = Mid, 2 = High emitters
- Prints cluster info for debugging and interpretation

**Result:** Each country receives a `cluster` label (Low/Mid/High emitters)

**Example:**
```
Country    | avg_co2 | cluster
-----------|---------|--------
Portugal   | 52.3    | 1 (Mid)
USA        | 5000.0  | 2 (High)
Chad       | 2.5     | 0 (Low)
```

**Cluster Interpretation:**
- **Cluster 0 (Low):** Low CO2 emitters
- **Cluster 1 (Mid):** Medium CO2 emitters
- **Cluster 2 (High):** High CO2 emitters

**Note:** Cluster labels are now guaranteed to match emission levels, not arbitrary K-means output.

---

### 7️⃣ **Save to PostgreSQL** (lines 146-173)

```python
# Prepare data
results_for_db = results.select(
    "country", "iso_code", "avg_co2", "avg_co2_per_capita", 
    "avg_gdp", "avg_population", "cluster"
).withColumn("batch_id", lit(batch_id))

# Save main table
save_to_postgresql(results_for_db, batch_id, "co2_clusters")

# Statistics per cluster
cluster_stats = results.groupBy("cluster").agg(
    count("*").alias("num_countries"),
    avg("avg_co2").alias("avg_co2_cluster"),
    ...
)
save_to_postgresql(cluster_stats, batch_id, "cluster_stats")
```

**What it does:**
- Selects relevant columns
- Adds `batch_id` (processing identifier)
- Saves to 2 tables:
  1. **`co2_clusters`:** Each country with its cluster
  2. **`cluster_stats`:** Averages per cluster

---

## 🔄 Continuous Loop (lines 272-277)

```python
query = kafka_stream.writeStream \
    .outputMode("update") \
    .foreachBatch(process_clustering) \
    .trigger(processingTime="15 seconds") \
    .start()
```

**What it does:**
- Every **15 seconds**, calls `process_clustering()`
- Processes accumulated batch of messages
- Infinite loop (until Ctrl+C)

---

## 📊 Complete Visual Summary

```
┌─────────────────────────────────────────────────────────┐
│ KAFKA (JSON messages from countries)                   │
└─────────────────────┬───────────────────────────────────┘
                      │ Streaming (15s batches)
                      ↓
┌─────────────────────────────────────────────────────────┐
│ SPARK CONSUMER                                          │
│                                                         │
│  1. Parse JSON         → DataFrame                     │
│  2. Clean NaNs         → Remove aggregates             │
│  3. Group by country   → Averages (CO2, GDP, pop)      │
│  4. Normalize          → StandardScaler                │
│  5. K-means (k=3)      → Assign clusters 0/1/2         │
│  6. Save PostgreSQL    → co2_clusters, cluster_stats   │
│                                                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│ POSTGRESQL                                              │
│  ├─ co2_clusters (country + cluster)                   │
│  └─ cluster_stats (averages per cluster)               │
└─────────────────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│ SUPERSET (reads and visualizes)                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Concepts

### **1. Streaming**
Instead of processing everything at once, processes **continuously** every 15s.

### **2. K-means**
Algorithm that groups similar data automatically (unsupervised).

### **3. StandardScaler**
Normalizes values so all variables have the same "weight" in clustering.

### **4. Pipeline**
Sequence of transformations (assembler → scaler → kmeans) executed automatically.