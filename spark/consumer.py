from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, count as count_func, countDistinct, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
import time

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

def process_clustering(batch_df, batch_id):
    start_time = time.time()
    record_count = batch_df.count()
    
    if record_count == 0:
        print(f"batch {batch_id}: no data in this batch")
        return
    
    print(f"processing batch {batch_id} with {record_count} records")
    
    try:  # lets try to process the data
        all_data = batch_df
        initial_count = all_data.count()
        print(f"Initial records in batch: {initial_count}")

        # Convert string "NaN" to NULL for numeric columns
        # Pandas sends NaN as string "NaN" in JSON, but Spark needs NULL for avg()
        from pyspark.sql.functions import when
        
        numeric_cols = ["gdp", "population", "co2", "co2_per_capita"]
        for col_name in numeric_cols:
            all_data = all_data.withColumn(
                col_name,
                when((col(col_name) == "NaN") | (col(col_name).isNull()), None)
                .otherwise(col(col_name).cast("double"))
            )
        
        # Filter ONLY aggregates (iso_code = NULL, "NaN", or '"NaN"' with quotes)
        # iso_code NULL or "NaN" means aggregates like "World", "Europe", etc.
        all_data = all_data.filter(
            (col("iso_code").isNotNull()) & 
            (col("iso_code") != "NaN") &
            (col("iso_code") != '"NaN"')  # Also filter the string with literal quotes
        )
        after_iso_filter = all_data.count()
        removed_aggregates = initial_count - after_iso_filter
        if removed_aggregates > 0:
            print(f"Removed {removed_aggregates} aggregate records (World, continents, etc.)")
        
        print(f"Records to process: {after_iso_filter}")
        
        if after_iso_filter == 0:
            print(f"Batch {batch_id}: No data after filtering aggregates")
            return
        
        # Note: NaN values will be handled by aggregation (avg ignores NaN)
        # and then filtered out at line ~121 with country_stats.na.drop()
        
        # Group by country with complete data
        country_stats = all_data.groupBy("country", "iso_code").agg(
            avg("co2").alias("avg_co2"),
            avg("co2_per_capita").alias("avg_co2_per_capita"),
            avg("gdp").alias("avg_gdp"),
            avg("population").alias("avg_population"),
            count_func("*").alias("data_points"),
            avg("year").alias("avg_year")  # to understand the temporal range of the data
        ).filter((col("avg_co2").isNotNull()) & (col("avg_co2_per_capita").isNotNull()) & (col("data_points") >= 5))
        
        countries_count = country_stats.count()
        #print(f"countries with sufficient data: {countries_count}")
        
        if countries_count < 3: # we need at least 3 countries to perform clustering    
            print(f"batch {batch_id}: not enough countries for clustering (need 3, got {countries_count})")
            
            # save data for debugging
            debug_data = country_stats.withColumn("batch_id", lit(batch_id))
            save_to_postgresql(debug_data, batch_id, "debug_country_stats")
            return
        
        print("sample country statistics:")  # lets see some data for debugging
        country_stats.orderBy(col("avg_co2").desc()).show(5)
        
        feature_cols = ["avg_co2", "avg_co2_per_capita", "avg_gdp", "avg_population"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        
        cleaned_data = country_stats.na.drop()  # bye bye null values
        
        if cleaned_data.count() < 3:
            print(f"batch {batch_id}: not enough data after cleaning")
            return
        
        # scale features
        scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
        
        # K-means with dynamic k (2-4 clusters)
        #k = min(4, max(2, cleaned_data.count() // 3)) 
        k = 3 
        print(f"{k} clusters for {cleaned_data.count()} countries")
        
        kmeans = KMeans(
            k=k, 
            featuresCol="scaled_features", 
            predictionCol="cluster",
            seed=42,
            maxIter=20
        )
        
        pipeline = Pipeline(stages=[assembler, scaler, kmeans])
        model = pipeline.fit(cleaned_data)  # train the model
        results = model.transform(cleaned_data)
        
        # prepare data for PostgreSQL
        results_for_db = results.select(
            "country", "iso_code", "avg_co2", "avg_co2_per_capita", 
            "avg_gdp", "avg_population", "cluster"
        ).withColumn("batch_id", lit(batch_id))
        
        # statistics of the clusters
        cluster_stats = results.groupBy("cluster").agg(
            count_func("*").alias("num_countries"),
            avg("avg_co2").alias("avg_co2_cluster"),
            avg("avg_co2_per_capita").alias("avg_co2_per_capita_cluster"),
            avg("avg_gdp").alias("avg_gdp_cluster")
        ).withColumn("batch_id", lit(batch_id))
        
        print("cluster statistics:")
        cluster_stats.show()
        
        print("top countries per cluster:")
        for cluster_id in range(k):
            cluster_countries = results.filter(col("cluster") == cluster_id) \
                .select("country", "avg_co2", "avg_co2_per_capita", "avg_gdp") \
                .orderBy(col("avg_co2").desc())
            
            print(f"cluster {cluster_id} (top 5 by CO2):")
            cluster_countries.show(5, truncate=False)
        
        print("saving to postgreSQL!!")
        save_to_postgresql(results_for_db, batch_id, "co2_clusters")
        save_to_postgresql(cluster_stats, batch_id, "cluster_stats")
        
        # --- TEMPORAL CLUSTERING (New Feature) ---
        print("--- starting temporal clustering (by year) ---")
        
        # Group by country AND year
        temporal_data = all_data.groupBy("country", "iso_code", "year").agg(
            avg("co2").alias("co2"),
            avg("co2_per_capita").alias("co2_per_capita"),
            avg("gdp").alias("gdp"),
            avg("population").alias("population")
        ).na.drop() # Remove records with missing values
        
        if temporal_data.count() > 10: # Only run if we have enough data points
            # Reuse feature columns but map to new names
            # Note: assembler expects inputCols to match dataframe columns
            temporal_assembler = VectorAssembler(
                inputCols=["co2", "co2_per_capita", "gdp", "population"], 
                outputCol="features"
            )
            
            # Reuse scaler and kmeans logic
            temporal_scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
            
            temporal_kmeans = KMeans(
                k=3, # Keep k=3 for consistency
                featuresCol="scaled_features", 
                predictionCol="cluster",
                seed=42
            )
            
            temporal_pipeline = Pipeline(stages=[temporal_assembler, temporal_scaler, temporal_kmeans])
            temporal_model = temporal_pipeline.fit(temporal_data)
            temporal_results = temporal_model.transform(temporal_data)
                
            # Select columns for DB
            temporal_results_db = temporal_results.select(
                "country", "iso_code", "year", "co2", "co2_per_capita", 
                "gdp", "population", "cluster"
            ).withColumn("batch_id", lit(batch_id))
            
            print(f"saving {temporal_results_db.count()} temporal records to co2_clustering_temporal")
            save_to_postgresql(temporal_results_db, batch_id, "co2_clustering_temporal")
        else:
            print("not enough temporal data for clustering")

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
            .option("kafka.client.id", "spark-consumer") \
            .option("kafka.group.id", "spark-clustering-group") \
            .load()
        
        print("connected to Kafka at kafka:9092")
        
        # transform json data
        json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")
        processed_stream_df = json_df.select(
            from_json(col("json_string"), schema).alias("data")
        ).select("data.*")
        
        # Basic validation - detailed filtering happens in process_clustering()
        filtered_df = processed_stream_df.filter(
            (col("year").isNotNull()) & 
            (col("country").isNotNull())
            # Note: iso_code and critical values filtering happens in process_clustering()
        )
        
        print("data processing pipeline created")
        return filtered_df
        
    except Exception as e:
        print(f"failed to create Kafka stream: {str(e)}")
        raise

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
        .option("checkpointLocation", "/tmp/checkpoints") \
        .trigger(processingTime="15 seconds") \
        .start()
    
    print("press ctrl+c to stop")
    
    query.awaitTermination()
    
except Exception as e:
    print(f"failed to start Spark Streaming: {str(e)}")
    spark.stop()