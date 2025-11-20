from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, avg, count as count_func, countDistinct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
import time

print("🚀 Initializing Spark Streaming Application...")

# 1. Iniciar a Spark Session com mais configurações
spark = SparkSession.builder \
    .appName("CO2EmissionsClustering") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.streaming.kafka.maxRatePerPartition", "100") \
    .getOrCreate()

# Reduzir o nível de logs
spark.sparkContext.setLogLevel("WARN")

print("✅ Spark session created successfully")

# 2. Definir o Schema dos Dados (baseado nos dados reais do Kafka)
schema = StructType([
    StructField("country", StringType(), True),
    StructField("year", IntegerType(), True),
    StructField("iso_code", StringType(), True),
    StructField("population", DoubleType(), True),
    StructField("gdp", DoubleType(), True),
    StructField("co2", DoubleType(), True),
    StructField("co2_per_capita", DoubleType(), True)
])

def process_batch_debug(batch_df, batch_id):
    """
    Função simples para debug - apenas mostra os dados recebidos
    """
    record_count = batch_df.count()  # ✅ Renomeado para evitar conflito
    print(f"📦 Batch {batch_id}: Received {record_count} records")
    
    if record_count > 0:
        print("Sample data:")
        batch_df.select("country", "year", "co2").show(5, truncate=False)
        
        # ✅ CORREÇÃO: Usar count_func em vez de count
        stats = batch_df.agg(
            count_func("*").alias("total_count"),
            countDistinct("country").alias("unique_countries"),
            avg("co2").alias("avg_co2")
        ).collect()[0]
        
        print(f"📊 Stats - Total: {stats['total_count']}, Countries: {stats['unique_countries']}, Avg CO2: {stats['avg_co2']:.4f}")

def process_clustering(batch_df, batch_id):
    """
    Função para processar cada batch de dados e aplicar clustering
    """
    start_time = time.time()
    record_count = batch_df.count()
    
    if record_count == 0:
        print(f"⏭️  Batch {batch_id}: No data in this batch")
        return
    
    print(f"🔍 Processing batch {batch_id} with {record_count} records")
    
    try:
        # Primeiro, vamos apenas fazer uma análise simples
        recent_data = batch_df.filter(col("year") >= 2000)
        
        if recent_data.count() == 0:
            print(f"📭 Batch {batch_id}: No recent data (after 2000)")
            return
        
        # Análise simples por país
        country_analysis = recent_data.groupBy("country").agg(
            count_func("*").alias("record_count"),  # ✅ CORREÇÃO AQUI TAMBÉM
            avg("co2").alias("avg_co2"),
            avg("co2_per_capita").alias("avg_co2_per_capita"),
            avg("gdp").alias("avg_gdp")
        ).filter(col("record_count") >= 1)
        
        print(f"🌍 Analyzed {country_analysis.count()} countries")
        
        # Mostrar os países com maior CO2
        top_emitters = country_analysis.orderBy(col("avg_co2").desc()).limit(10)
        
        print(f"\n🏆 TOP 10 CO2 EMITTERS - Batch {batch_id}:")
        top_emitters.select("country", "avg_co2", "avg_co2_per_capita", "avg_gdp").show(truncate=False)
        
        # Tempo de processamento
        processing_time = time.time() - start_time
        print(f"✅ Batch {batch_id} completed in {processing_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error in batch {batch_id}: {str(e)}")
        import traceback
        traceback.print_exc()

# 3. Ler os Dados do Kafka
def create_kafka_stream():
    print("🔗 Connecting to Kafka...")
    
    try:
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "emissions-topic") \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        print("✅ Connected to Kafka successfully")
        
        # Transformar os dados JSON
        json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")
        processed_stream_df = json_df.select(
            from_json(col("json_string"), schema).alias("data")
        ).select("data.*")
        
        # Filtrar e limpar dados
        filtered_df = processed_stream_df.filter(
            (col("year").isNotNull()) & 
            (col("co2").isNotNull()) &
            (col("country").isNotNull())
        )
        
        print("✅ Data processing pipeline created")
        return filtered_df
        
    except Exception as e:
        print(f"❌ Failed to create Kafka stream: {str(e)}")
        raise

# 4. Iniciar o Stream Processing
try:
    print("="*60)
    print("🚀 CO2 EMISSIONS SPARK STREAMING APPLICATION")
    print("="*60)
    print("📊 Source: Kafka topic 'emissions-topic'")
    print("🔗 Kafka: kafka:9092")
    print("⏱️  Processing: Every 30 seconds")
    print("="*60)
    
    kafka_stream = create_kafka_stream()
    
    # Iniciar com função de debug primeiro
    query = kafka_stream.writeStream \
        .outputMode("update") \
        .foreachBatch(process_batch_debug) \
        .option("checkpointLocation", "/tmp/checkpoints") \
        .trigger(processingTime="30 seconds") \
        .start()
    
    print("🎯 Spark Streaming started successfully!")
    print("⏳ Waiting for data from Kafka...")
    print("💡 Press Ctrl+C to stop")
    
    query.awaitTermination()
    
except Exception as e:
    print(f"💥 Failed to start Spark Streaming: {str(e)}")
    import traceback
    traceback.print_exc()
    spark.stop()