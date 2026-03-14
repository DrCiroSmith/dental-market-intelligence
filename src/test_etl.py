from data_pipeline.demographics_etl import DemographicsETL
import pandas as pd

try:
    etl = DemographicsETL()
    df = etl.extract_raw_data("market_data.csv")
    
    # Calculate saturation first
    df['saturation_index'] = etl.calculate_saturation_index(df['population'], df['active_dentists'])
    
    # Run the scoring algorithm ByteRover wrote
    scored_df = etl.score_market_viability(df)
    
    print("\n--- TESTING DEMOGRAPHICS ETL ALGORITHM ---")
    print(scored_df[['zip_code', 'saturation_index', 'median_income', 'market_score']])
except Exception as e:
    print(f"\nError running ETL: {e}")
