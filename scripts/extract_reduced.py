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

def preprocess_co2_data(input_path: str, output_path: str):

    print(f"loading data from '{input_path}'")
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"input file '{input_path}' was not found")
        return

    # as decided during the exploratory analysis, we don't need all the original columns.
    columns_to_keep = ["country", "year", "iso_code", "population", "gdp", "co2", "co2_per_capita"]
        
    df_filtered = df[columns_to_keep]

    # we'll filter the records to include only data from 1900 onwards (up to 2024). 
    df_final = df_filtered[df_filtered['year'] >= 1900].copy()
    df_final = df_final[df_filtered['year'] <= 2024].copy()

    # time to save our work! 
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    df_final.to_csv(output_path, index=False)
    print(f"the final dataset contains {df_final.shape[0]} rows and {df_final.shape[1]} columns")

if __name__ == '__main__':
    input_file = '../data/owid-co2-data.csv'
    output_file = '../data/reduced_co2.csv'
    
    preprocess_co2_data(input_file, output_file)