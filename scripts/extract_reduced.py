#!/usr/bin/env python3
"""
Extract reduced CO2 dataset with only 7 core columns.
Performs basic cleaning and saves to data/reduced_co2.csv
"""

import pandas as pd
import os

# Columns to keep
COLUMNS = [
    "country",
    "year", 
    "iso_code",
    "population",
    "gdp",
    "co2",
    "co2_per_capita"
]

def main():
    print("Loading full dataset...")
    input_file = "../data/owid-co2-data.csv"
    output_dir = "../data"
    output_file = os.path.join(output_dir, "reduced_co2.csv")
    
    # Read only the columns we need
    df = pd.read_csv(input_file, usecols=COLUMNS)
    
    print(f"Original rows: {len(df)}")
    print(f"Original columns: {len(df.columns)}")
    
    # Basic cleaning - require country, year, and co2
    print("\nCleaning data...")
    df_clean = df.dropna(subset=["country", "year", "co2"])
    
    # Filter to more recent years (better data quality)
    df_clean = df_clean[df_clean['year'] >= 1900]
    
    print(f"After cleaning: {len(df_clean)} rows")
    print(f"Removed: {len(df) - len(df_clean)} rows")
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Save reduced dataset
    df_clean.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    # Show summary statistics
    print("\n=== Dataset Summary ===")
    print(df_clean.info())
    print("\n=== First 5 rows ===")
    print(df_clean.head())
    print("\n=== Sample countries ===")
    print(df_clean['country'].value_counts().head(10))
    
    print(f"\n✓ Extraction complete!")

if __name__ == "__main__":
    main()
