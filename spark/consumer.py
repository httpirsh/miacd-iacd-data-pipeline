from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType


def save_to_postgresql(df, table_name, batch_id):
    df.write.mode("append").jdbc(
        url="jdbc:postgresql://postgres:5432/co2_data",
        table=table_name,
        properties={"user": "co2_user", "password": "co2_password", 
                    "driver": "org.postgresql.Driver"
        }
    )
    print(f"batch #{batch_id} successfully saved to table '{table_name}'")


def process_batch(batch_df, batch_id):
    print(f"processing batch #{batch_id}")

    if batch_df.count() == 0:
        print("empty batch, waiting for more data")
        return

    # clean null data in key columns
    cleaned_batch = batch_df.na.drop(subset=["country", "year", "iso_code"])

    if cleaned_batch.count() == 0:
        print("no valid data in batch after cleaning.")
        return

    # Save raw emissions data
    save_to_postgresql(cleaned_batch, "raw_emissions", batch_id)
    
    print(f"Saved {cleaned_batch.count()} records to raw_emissions")


# - - - - - - - -
# start spark session
spark = SparkSession.builder \
    .appName("co2emissionsstreaming") \
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
    .option("subscribe", "co2-raw") \
    .option("startingOffsets", "earliest") \
    .load()

print("reading from kafka topic 'co2-raw'")

# transform data
json_df = kafka_df.selectExpr("cast(value as string) as json_string")
processed_stream_df = json_df.select(from_json(col("json_string"), schema).alias("data")).select("data.*")

# Filter for quality data (1900-2024)
filtered_df = processed_stream_df.filter((col("year") >= 1900) & (col("year") <= 2024))

# start streaming query
query = filtered_df.writeStream \
    .foreachBatch(process_batch) \
    .trigger(processingTime='30 seconds') \
    .option("checkpointLocation", "/tmp/spark-checkpoints") \
    .start()

print("streaming query started, waiting for data...")
query.awaitTermination()

