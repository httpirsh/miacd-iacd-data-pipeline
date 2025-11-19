#!/usr/bin/env python3
"""
Spark Batch Processing Job for CO2 Data
Reads reduced CSV, cleans data, and writes to PostgreSQL
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum as spark_sum, max as spark_max, min as spark_min, count, year as spark_year
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL connection configuration
POSTGRES_URL = "jdbc:postgresql://postgres.default.svc.cluster.local:5432/co2_data"
POSTGRES_PROPERTIES = {
    "user": "co2_user",
    "password": "co2_password",
    "driver": "org.postgresql.Driver"
}

def create_spark_session():
    """Create Spark session with PostgreSQL driver."""
    return SparkSession.builder \
        .appName("CO2-Data-Processing") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def load_data(spark, csv_path):
    """Load reduced CO2 dataset."""
    logger.info(f"Loading data from {csv_path}")
    
    schema = StructType([
        StructField("country", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("iso_code", StringType(), True),
        StructField("population", DoubleType(), True),
        StructField("gdp", DoubleType(), True),
        StructField("co2", DoubleType(), True),
        StructField("co2_per_capita", DoubleType(), True)
    ])
    
    df = spark.read.csv(csv_path, header=True, schema=schema)
    logger.info(f"Loaded {df.count()} rows")
    return df

def clean_data(df):
    """Basic data cleaning operations."""
    logger.info("Cleaning data...")
    
    # Filter out rows with missing critical fields
    df_clean = df.filter(
        (col("country").isNotNull()) & 
        (col("year").isNotNull()) & 
        (col("co2").isNotNull())
    )
    
    # Fill missing iso_code with 'UNKNOWN'
    df_clean = df_clean.fillna({"iso_code": "UNKNOWN"})
    
    logger.info(f"After cleaning: {df_clean.count()} rows")
    return df_clean

def create_country_summary(df):
    """Aggregate data by country."""
    logger.info("Creating country summary...")
    
    summary = df.groupBy("country", "iso_code").agg(
        spark_sum("co2").alias("total_co2"),
        avg("co2").alias("avg_co2"),
        spark_max("co2").alias("max_co2"),
        spark_min("year").alias("first_year"),
        spark_max("year").alias("last_year"),
        count("*").alias("record_count"),
        avg("co2_per_capita").alias("avg_co2_per_capita"),
        spark_sum("population").alias("total_population_years")
    )
    
    # Order by total CO2 descending
    summary = summary.orderBy(col("total_co2").desc())
    
    logger.info(f"Country summary: {summary.count()} countries")
    return summary

def create_yearly_summary(df):
    """Aggregate data by year."""
    logger.info("Creating yearly summary...")
    
    summary = df.groupBy("year").agg(
        spark_sum("co2").alias("global_co2"),
        avg("co2").alias("avg_country_co2"),
        count("country").alias("num_countries"),
        spark_sum("population").alias("total_population"),
        avg("co2_per_capita").alias("avg_co2_per_capita"),
        spark_max("co2").alias("max_country_co2")
    )
    
    # Order by year
    summary = summary.orderBy("year")
    
    logger.info(f"Yearly summary: {summary.count()} years")
    return summary

def write_to_postgres(df, table_name, mode="overwrite"):
    """Write dataframe to PostgreSQL."""
    logger.info(f"Writing to PostgreSQL table: {table_name}")
    
    df.write \
        .jdbc(POSTGRES_URL, table_name, mode=mode, properties=POSTGRES_PROPERTIES)
    
    logger.info(f"✓ Data written to {table_name}")

def main():
    logger.info("=== Starting CO2 Data Processing Job ===")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Load data
        csv_path = "/tmp/reduced_co2.csv"
        df_raw = load_data(spark, csv_path)
        
        # Clean data
        df_clean = clean_data(df_raw)
        
        # Show sample
        logger.info("Sample cleaned data:")
        df_clean.show(5)
        
        # Write raw cleaned data to PostgreSQL
        write_to_postgres(df_clean, "raw_emissions")
        
        # Create and write country summary
        df_country = create_country_summary(df_clean)
        df_country.show(10)
        write_to_postgres(df_country, "country_summary")
        
        # Create and write yearly summary
        df_yearly = create_yearly_summary(df_clean)
        df_yearly.show(10)
        write_to_postgres(df_yearly, "yearly_summary")
        
        logger.info("=== Processing Complete ===")
        
    except Exception as e:
        logger.error(f"Job failed: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
