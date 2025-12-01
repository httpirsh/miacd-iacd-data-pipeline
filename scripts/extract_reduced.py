#!/usr/bin/env python3

# this script is a Python alternative to the 'eda.ipynb' notebook
# its goal is to perform the necessary data extraction and preprocessing steps
# to generate the final, reduced dataset directly, without the need for manual exploratory analysis
#
# the output dataset (reduced_co2.csv) will be used by:
# - kafka/producer.py: to stream data into Kafka topic "emissions-topic"
# - spark/consumer.py: to perform K-means clustering (k=3) and store results in PostgreSQL
# - postgres database: co2_emissions (user: postgres, password: postgres)

import pandas as pd
import os

def preprocess_co2_data(input_path, output_path):

    print(f"loading data from '{input_path}'")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"input file '{input_path}' was not found")
        return

    print(f"  - Original shape: {df.shape[0]:,} rows, {df.shape[1]} columns")

    # as decided during the exploratory analysis, we dont need all the original columns.
    columns_to_keep = ["country", "year", "iso_code", "population", "gdp", "co2", "co2_per_capita"]
        
    df_filtered = df[columns_to_keep]

    # filter the records by date (1900-2022)
    df_final = df_filtered[df_filtered['year'] >= 1900].copy()
    df_final = df_final[df_final['year'] <= 2022].copy()  # we dont have any values of gdp after 2022
    
    # remove aggregate entities (keep only countries with iso_code)
    df_final = df_final.dropna(subset=['iso_code'])

    # time to save our work! 
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    df_final.to_csv(output_path, index=False)
    
    # print statistics
    print()
    print(f"dataset saved to '{output_path}'")
    print(f"rows: {df_final.shape[0]:,}")
    print(f"columns: {df_final.shape[1]}")
    print(f"year range: {df_final['year'].min():.0f}-{df_final['year'].max():.0f}")
    print(f"unique countries: {df_final['country'].nunique()}")
    print(f"file size: {os.path.getsize(output_path) / 1024:.1f} KB")

if __name__ == '__main__':
    input_file = '../data/owid-co2-data.csv'
    output_file = '../data/reduced_co2.csv'
    
    preprocess_co2_data(input_file, output_file)