"""
Spark Consumer for CO2 Emissions Data
Reads from Kafka, processes data, and writes to PostgreSQL
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CO2SparkConsumer:
    def __init__(self, kafka_servers='localhost:9092', kafka_topic='co2-raw',
                 postgres_url='jdbc:postgresql://localhost:5432/co2_data',
                 postgres_user='co2_user', postgres_password='co2_password'):
        """
        Initialize Spark consumer
        
        Args:
            kafka_servers: Kafka broker address
            kafka_topic: Kafka topic to consume from
            postgres_url: PostgreSQL JDBC URL
            postgres_user: PostgreSQL username
            postgres_password: PostgreSQL password
        """
        self.kafka_servers = kafka_servers
        self.kafka_topic = kafka_topic
        self.postgres_url = postgres_url
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        
        # Create Spark session
        self.spark = SparkSession.builder \
            .appName("CO2DataConsumer") \
            .config("spark.jars.packages", 
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                    "org.postgresql:postgresql:42.6.0") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark session initialized")
    
    def define_schema(self):
        """Define schema for CO2 data (7 columns only)"""
        return StructType([
            StructField("country", StringType(), True),
            StructField("year", IntegerType(), True),
            StructField("iso_code", StringType(), True),
            StructField("population", DoubleType(), True),
            StructField("gdp", DoubleType(), True),
            StructField("co2", DoubleType(), True),
            StructField("co2_per_capita", DoubleType(), True)
        ])
    
    def read_from_kafka(self):
        """Read streaming data from Kafka"""
        logger.info(f"Reading from Kafka topic: {self.kafka_topic}")
        
        df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_servers) \
            .option("subscribe", self.kafka_topic) \
            .option("startingOffsets", "earliest") \
            .load()
        
        # Parse JSON data
        schema = self.define_schema()
        parsed_df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")
        
        return parsed_df
    
    def write_to_postgres(self, df, table_name, mode="append"):
        """
        Write DataFrame to PostgreSQL
        
        Args:
            df: DataFrame to write
            table_name: Target table name
            mode: Write mode (append, overwrite)
        """
        df.write \
            .format("jdbc") \
            .option("url", self.postgres_url) \
            .option("dbtable", table_name) \
            .option("user", self.postgres_user) \
            .option("password", self.postgres_password) \
            .option("driver", "org.postgresql.Driver") \
            .mode(mode) \
            .save()
        
        logger.info(f"Data written to {table_name}")
    
    def start_streaming(self):
        """Start streaming from Kafka to PostgreSQL"""
        logger.info("Starting streaming pipeline...")
        
        # Read from Kafka
        stream_df = self.read_from_kafka()
        
        # Write to PostgreSQL using foreachBatch
        query = stream_df.writeStream \
            .foreachBatch(lambda batch_df, batch_id: 
                         self.write_to_postgres(batch_df, "raw_emissions", mode="append")) \
            .outputMode("append") \
            .trigger(processingTime='10 seconds') \
            .start()
        
        logger.info("Streaming started. Waiting for data...")
        query.awaitTermination()
    
    def stop(self):
        """Stop Spark session"""
        self.spark.stop()
        logger.info("Spark session stopped")


def main():
    """Main function to run the consumer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Consume CO2 data from Kafka')
    parser.add_argument('--kafka-servers', type=str, default='localhost:9092',
                        help='Kafka broker address')
    parser.add_argument('--kafka-topic', type=str, default='co2-raw',
                        help='Kafka topic name')
    parser.add_argument('--postgres-url', type=str, 
                        default='jdbc:postgresql://localhost:5432/co2_data',
                        help='PostgreSQL JDBC URL')
    parser.add_argument('--postgres-user', type=str, default='co2_user',
                        help='PostgreSQL username')
    parser.add_argument('--postgres-password', type=str, default='co2_password',
                        help='PostgreSQL password')
    
    args = parser.parse_args()
    
    # Create and start consumer
    consumer = CO2SparkConsumer(
        kafka_servers=args.kafka_servers,
        kafka_topic=args.kafka_topic,
        postgres_url=args.postgres_url,
        postgres_user=args.postgres_user,
        postgres_password=args.postgres_password
    )
    
    try:
        consumer.start_streaming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        consumer.stop()


if __name__ == '__main__':
    main()
