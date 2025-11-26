from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, count as count_func, countDistinct, lit, current_timestamp, min, max
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql.functions import when
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
import time


def save_to_postgresql(df, batch_id, table_name):

    try:  # lets try to save the data to PostgreSQL
        jdbc_url = "jdbc:postgresql://postgres:5432/co2_emissions"
        connection_properties = {
            "user": "postgres",
            "password": "postgres",
            "driver": "org.postgresql.Driver"
        }
        
        df.write.mode("append").jdbc(url=jdbc_url, table=table_name, properties=connection_properties)
        
        print(f"batch {batch_id} saved to PostgreSQL table '{table_name}' ({df.count()} records)")
        return True
        
    except Exception as e:
        print(f"failed to save batch {batch_id} to postgreSQL: {str(e)}")
        return False


def clean_data(df):
    
    # 1st we convert "NaN" to NULL for numeric columns --> because avg ignores NULL
    numeric_cols = ["gdp", "population", "co2", "co2_per_capita"]
    for col_name in numeric_cols:
        df = df.withColumn(col_name,
            when((col(col_name) == "NaN") | (col(col_name).isNull()), None)
            .otherwise(col(col_name).cast("double"))
        )
    
    # as seen in exploratory data, iso_code is NULL for aggregate records (World, continents, etc)
    df = df.filter((col("iso_code").isNotNull()) & (col("iso_code") != "NaN") & (col("iso_code") != '"NaN"'))
    
    return df


def aggregate_by_country(df):
    country_stats = df.groupBy("country", "iso_code").agg(
        # we calculate the average of the numeric columns
        avg("co2").alias("avg_co2"),
        avg("co2_per_capita").alias("avg_co2_per_capita"),
        avg("gdp").alias("avg_gdp"),
        avg("population").alias("avg_population"),
        count_func("*").alias("data_points"),
        
        # we considere the temporal context
        min("year").alias("first_year"),
        max("year").alias("last_year"),
        avg(when(col("year") >= 2010, col("co2"))).alias("avg_co2_recent")
    
    ).filter(
        (col("avg_co2").isNotNull()) & 
        (col("avg_co2_per_capita").isNotNull()) & 
        (col("data_points") >= 5)
    )
    
    return country_stats


def perform_clustering(df, k=3):

    cleaned_data = df.na.drop()  # bye bye NaN values
    
    if cleaned_data.count() < k:  # if there are less than k countries, we can't perform clustering
        return None, None
    
    # prepare features for clustering
    feature_cols = ["avg_co2", "avg_co2_per_capita", "avg_gdp", "avg_population"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
    
    kmeans = KMeans(k=k, 
                    featuresCol="scaled_features", predictionCol="cluster", 
                    seed=42, maxIter=20)
    
    # create and fit pipeline
    pipeline = Pipeline(stages=[assembler, scaler, kmeans])
    model = pipeline.fit(cleaned_data)
    results = model.transform(cleaned_data)
    
    print(f"{k} clusters for {cleaned_data.count()} countries")
    
    return results, cleaned_data.count()


def calculate_cluster_stats(results):
    # simply statistic by cluster
    cluster_stats = results.groupBy("cluster").agg(
        count_func("*").alias("num_countries"),
        avg("avg_co2").alias("avg_co2_cluster"),
        avg("avg_co2_per_capita").alias("avg_co2_per_capita_cluster"),
        avg("avg_gdp").alias("avg_gdp_cluster")
    )
    return cluster_stats


def show_cluster_results(results, k):
    results.groupBy("cluster").agg(
        count_func("*").alias("countries"),
        avg("avg_co2").alias("avg_co2")
    ).show()
    
    print("top countries per cluster:")
    for cluster_id in range(k):
        cluster_countries = results.filter(col("cluster") == cluster_id) \
            .select("country", "avg_co2", "avg_co2_per_capita", "avg_gdp") \
            .orderBy(col("avg_co2").desc())
        
        print(f"cluster {cluster_id} (top 5 by CO2):")
        cluster_countries.show(5, truncate=False)


def process_clustering(batch_df, batch_id):

    #  - orchestrates data cleaning, 
    #  - aggregation, 
    #  - clustering

    start_time = time.time()
    record_count = batch_df.count()
    
    if record_count == 0:
        print(f"batch {batch_id}: no data in this batch")
        return
    
    print(f"processing batch {batch_id} with {record_count} records")
    
    try:
        all_data = clean_data(batch_df)  # step 1 - clean data
        #print(f"records to process: {all_data.count()}")
        
        if all_data.count() == 0:
            print(f"batch {batch_id}: no data after filtering aggregates")
            return
        
        country_stats = aggregate_by_country(all_data)  # step 2 - aggregate by country
        countries_count = country_stats.count()
        
        if countries_count < 3:
            print(f"batch {batch_id}: not enough countries for clustering (need 3, got {countries_count})")
            return
        
        results, num_countries = perform_clustering(country_stats, k=3)  # step 3 - perform clustering
        
        if results is None:
            print(f"batch {batch_id}: clustering failed")
            return
        
        cluster_stats = calculate_cluster_stats(results)  # step 4 - calculate cluster statistics
        
        show_cluster_results(results, k=3)  # step 5 - show results (debugging)
        
        results_for_db = results.select(
            "country", "iso_code", "avg_co2", "avg_co2_per_capita", 
            "avg_gdp", "avg_population", "data_points",
            "first_year", "last_year", "avg_co2_recent", "cluster"
        ).withColumn("batch_id", lit(batch_id))
        
        cluster_stats_db = cluster_stats.withColumn("batch_id", lit(batch_id))
        
        print("saving to postgreSQL!!")
        save_to_postgresql(results_for_db, batch_id, "co2_clusters")
        save_to_postgresql(cluster_stats_db, batch_id, "cluster_stats")

        processing_time = time.time() - start_time
        print(f"batch {batch_id} completed in {processing_time:.2f}s")
        
    except Exception as e:
        print(f"error in batch {batch_id}: {str(e)}")


def create_kafka_stream():
    # read data from kafka
    print("connecting to kafka...")
    
    try:
        # specific configuration to force correct connection
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "emissions-topic") \
            .option("startingOffsets", "earliest") \
            .load()
        
        print("connected to Kafka at kafka:9092")
        
        # transform json data
        json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")
        processed_stream_df = json_df.select(
            from_json(col("json_string"), schema).alias("data")
        ).select("data.*")
        
        # basic validation - detailed filtering happens in process_clustering()
        filtered_df = processed_stream_df.filter(
            (col("year").isNotNull()) & 
            (col("country").isNotNull())
        )
        
        print("data processing pipeline created")
        return filtered_df
        
    except Exception as e:
        print(f"failed to create Kafka stream: {str(e)}")
        raise


spark = SparkSession.builder.appName("CO2EmissionsClustering").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

print("spark session created successfully")

schema = StructType([
    StructField("country", StringType(), True),
    StructField("year", IntegerType(), True),
    StructField("iso_code", StringType(), True),
    StructField("population", DoubleType(), True),
    StructField("gdp", DoubleType(), True),
    StructField("co2", DoubleType(), True),
    StructField("co2_per_capita", DoubleType(), True)
])

try:  # lets try to process the data
    print("kafka topic 'emissions-topic'")
    print("--> kafka:9092")
    print("--> database: PostgreSQL (co2_emissions)")
    print("processing: Every 15 seconds")
    
    kafka_stream = create_kafka_stream()
    
    # start clustering
    query = kafka_stream.writeStream \
        .outputMode("update") \
        .foreachBatch(process_clustering) \
        .trigger(processingTime="15 seconds") \
        .start()
    
    print("press ctrl+c to stop")
    
    query.awaitTermination()
    
except Exception as e:
    print(f"failed to start Spark Streaming: {str(e)}")
    spark.stop()