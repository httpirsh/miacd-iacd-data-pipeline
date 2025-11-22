from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, count, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline


def save_to_postgresql(df, table_name, batch_id):
    df.write.mode("append").jdbc(
        url="jdbc:postgresql://postgres:5432/co2_emissions",
        table=table_name,
        properties={"user": "postgres", "password": "postgres", 
                    "driver": "org.postgresql.Driver"
        }
    )
    print(f"batch #{batch_id} successfully saved to table '{table_name}")


def process_batch(batch_df, batch_id):
    print(f"processing batch #{batch_id}")

    if batch_df.count() == 0:
        print("empty batch, waiting for more data")
        return

    # clean null data in key columns
    cleaned_batch = batch_df.na.drop(subset=["country", "iso_code", "co2", "co2_per_capita", "gdp", "population"])

    if cleaned_batch.count() == 0:
        print("no valid data in batch after cleaning.")
        return

    # aggregate data by country 
    country_stats = cleaned_batch.groupBy("country", "iso_code").agg(
        avg("co2").alias("avg_co2"),
        avg("co2_per_capita").alias("avg_co2_per_capita"),
        avg("gdp").alias("avg_gdp"),
        avg("population").alias("avg_population"),
        count("*").alias("data_points")  # count records per country in batch
    )

    if country_stats.count() < 3:  # k-means needs at least 'k' points
        print("not enough aggregated data for clustering.")
        return

    # machine learning pipeline
    feature_cols = ["avg_co2", "avg_co2_per_capita", "avg_gdp", "avg_population"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_vector")
    scaler = StandardScaler(inputCol="features_vector", outputCol="scaled_features")
    kmeans = KMeans(k=3, featuresCol="scaled_features", predictionCol="cluster", seed=42)
    pipeline = Pipeline(stages=[assembler, scaler, kmeans])

    # train and apply pipeline
    model = pipeline.fit(country_stats)
    results = model.transform(country_stats)

    print(f"clustering results (batch #{batch_id})")
    results.select("country", "avg_co2", "avg_gdp", "cluster").show()

    #  prepare final dataframe and save to postgresql
    final_df_to_save = results.select(
        "country", "iso_code", "avg_co2", "avg_co2_per_capita",
        "avg_gdp", "avg_population", "cluster"
    ).withColumn("batch_id", lit(batch_id))  # add batch id

    save_to_postgresql(final_df_to_save, "co2_clusters", batch_id)


# - - - - - - - -
# start spark session
spark = SparkSession.builder \
    .appName("co2emissionsclustering") \
    .getOrCreate()

spark.sparkContext.setLogLevel("warn")
print("--- spark session started ---")

schema = StructType([
    StructField("country", StringType(), True),
    StructField("year", IntegerType(), True),
    StructField("iso_code", StringType(), True),
    StructField("population", DoubleType(), True),
    StructField("gdp", DoubleType(), True),
    StructField("co2", DoubleType(), True),
    StructField("co2_per_capita", DoubleType(), True)
])

# read kafka stream
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka.default.svc.cluster.local:9092") \
    .option("subscribe", "emissions-topic") \
    .option("startingOffsets", "earliest") \
    .load()

print("reading from kafka topic 'emissions-topic'")

# transform data
json_df = kafka_df.selectExpr("cast(value as string) as json_string")
processed_stream_df = json_df.select(from_json(col("json_string"), schema).alias("data")).select("data.*")

filtered_df = processed_stream_df.filter((col("year") >= 1950) & (col("year") <= 2024))

# start streaming query
query = filtered_df.writeStream \
    .foreachBatch(process_batch) \
    .trigger(processingTime='30 seconds') \
    .option("checkpointLocation", "/tmp/spark-checkpoints") \
    .start()

print("streaming query started, waiting for data...")
query.awaitTermination()
