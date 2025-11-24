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
    """
    Função para guardar DataFrame no PostgreSQL
    """
    try:
        # Configuração de conexão com PostgreSQL
        jdbc_url = "jdbc:postgresql://postgres:5432/co2_emissions"
        connection_properties = {
            "user": "postgres",
            "password": "postgres",
            "driver": "org.postgresql.Driver"
        }
        
        # Escrever no PostgreSQL
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
    
    try:
        all_data = batch_df
        
        # Mostrar estatísticas dos dados recebidos
        print(f"year range in batch: {all_data.agg({'year': 'min'}).collect()[0][0]} - {all_data.agg({'year': 'max'}).collect()[0][0]}")
        print(f"unique countries in batch: {all_data.select('country').distinct().count()}")
        
        # ✅ CORREÇÃO: Agrupar por país com dados completos
        country_stats = all_data.groupBy("country", "iso_code").agg(
            avg("co2").alias("avg_co2"),
            avg("co2_per_capita").alias("avg_co2_per_capita"),
            avg("gdp").alias("avg_gdp"),
            avg("population").alias("avg_population"),
            count_func("*").alias("data_points"),
            avg("year").alias("avg_year")  # Para entender a temporalidade dos dados
        ).filter(
            # ✅ Apenas países com dados razoáveis
            (col("avg_co2").isNotNull()) &
            (col("avg_co2_per_capita").isNotNull()) &
            (col("data_points") >= 5)  # Pelo menos 5 anos de dados
        )
        
        countries_count = country_stats.count()
        #print(f"countries with sufficient data: {countries_count}")
        
        if countries_count < 3:
            print(f"batch {batch_id}: not enough countries for clustering (need 3, got {countries_count})")
            
            # Guardar dados para análise mesmo sem clustering
            debug_data = country_stats.withColumn("batch_id", lit(batch_id))
            save_to_postgresql(debug_data, batch_id, "debug_country_stats")
            return
        
        # ✅ MOSTRAR ALGUNS DADOS PARA DEBUG
        print("sample country statistics:")
        country_stats.orderBy(col("avg_co2").desc()).show(5)
        
        # Preparar features
        feature_cols = ["avg_co2", "avg_co2_per_capita", "avg_gdp", "avg_population"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        
        # Remover valores nulos
        cleaned_data = country_stats.na.drop()
        
        if cleaned_data.count() < 3:
            print(f"batch {batch_id}: not enough data after cleaning")
            return
        
        # Escalar features
        scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
        
        # K-means com k dinâmico (2-4 clusters)
        #k = min(4, max(2, cleaned_data.count() // 3)) 
        k=3 # Entre 2-4 clusters
        print(f"🎯 Using {k} clusters for {cleaned_data.count()} countries")
        
        kmeans = KMeans(
            k=k, 
            featuresCol="scaled_features", 
            predictionCol="cluster",
            seed=42,
            maxIter=20
        )
        
        # Pipeline
        pipeline = Pipeline(stages=[assembler, scaler, kmeans])
        
        # Treinar modelo
        model = pipeline.fit(cleaned_data)
        
        # Aplicar modelo
        results = model.transform(cleaned_data)
        
        # Preparar dados para PostgreSQL (Removido data_points e avg_year pois não existem na tabela)
        results_for_db = results.select(
            "country", "iso_code", "avg_co2", "avg_co2_per_capita", 
            "avg_gdp", "avg_population", "cluster"
        ).withColumn("batch_id", lit(batch_id))
        
        # Estatísticas dos clusters (Removido avg_population_cluster pois não existe na tabela)
        cluster_stats = results.groupBy("cluster").agg(
            count_func("*").alias("num_countries"),
            avg("avg_co2").alias("avg_co2_cluster"),
            avg("avg_co2_per_capita").alias("avg_co2_per_capita_cluster"),
            avg("avg_gdp").alias("avg_gdp_cluster")
        ).withColumn("batch_id", lit(batch_id))
        
        # Mostrar resultados        
        print("cluster statistics:")
        cluster_stats.show()
        
        print("top countries per cluster:")
        for cluster_id in range(k):
            cluster_countries = results.filter(col("cluster") == cluster_id) \
                .select("country", "avg_co2", "avg_co2_per_capita", "avg_gdp") \
                .orderBy(col("avg_co2").desc())
            
            print(f"cluster {cluster_id} (top 5 by CO2):")
            cluster_countries.show(5, truncate=False)
        
        # Guardar no PostgreSQL
        print("saving to postgreSQL!!")
        save_to_postgresql(results_for_db, batch_id, "co2_clusters")
        save_to_postgresql(cluster_stats, batch_id, "cluster_stats")
        
        processing_time = time.time() - start_time
        print(f"batch {batch_id} completed in {processing_time:.2f}s")
        
    except Exception as e:
        print(f"error in batch {batch_id}: {str(e)}")


# 3. Ler os Dados do Kafka com configuração específica
def create_kafka_stream():
    print("connecting to kafka...")
    
    try:
        # Configuração específica para forçar conexão correcta
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "emissions-topic") \
            .option("startingOffsets", "earliest") \
            .option("kafka.client.id", "spark-consumer") \
            .option("kafka.group.id", "spark-clustering-group") \
            .load()
        
        print("connected to Kafka at kafka:9092")
        
        # Transformar os dados JSON
        json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")
        processed_stream_df = json_df.select(
            from_json(col("json_string"), schema).alias("data")
        ).select("data.*")
        
        # Filtrar e limpar dados
        filtered_df = processed_stream_df.filter(
            (col("year").isNotNull()) & 
            (col("co2").isNotNull()) &
            (col("country").isNotNull()) &
            (col("iso_code").isNotNull())
        )
        
        print("data processing pipeline created")
        return filtered_df
        
    except Exception as e:
        print(f"failed to create Kafka stream: {str(e)}")
        raise

# 4. Iniciar o Stream Processing
try:
    print("📊 Source: Kafka topic 'emissions-topic'")
    print(" --> kafka:9092")
    print("--> database: PostgreSQL (co2_emissions)")
    print("processing: Every 15 seconds")
    
    kafka_stream = create_kafka_stream()
    
    # Iniciar o processamento com clustering
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