import pandas as pd
import numpy as np

class DemographicsETL:
    def __init__(self, raw_data_path: str = "data/raw/"):
        self.raw_data_path = raw_data_path

    def extract_raw_data(self, filename: str) -> pd.DataFrame:
        try:
            return pd.read_csv(f"{self.raw_data_path}{filename}")
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Returning empty DataFrame.")
            return pd.DataFrame()

    def calculate_saturation_index(self, population: pd.Series, active_dentists: pd.Series) -> pd.Series:
        safe_dentists = active_dentists.replace(0, np.nan)
        return population / safe_dentists

    def score_market_viability(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_to_score = ['median_income', 'population_growth', 'saturation_index']
        
        # Handle missing data by filling with the mean
        for col in cols_to_score:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mean())
        
        # Min-Max Scaling (Normalize values between 0 and 1)
        normalized = pd.DataFrame()
        for col in cols_to_score:
            if col in df.columns:
                min_val, max_val = df[col].min(), df[col].max()
                if max_val - min_val == 0:
                    normalized[col] = 1.0
                else:
                    normalized[col] = (df[col] - min_val) / (max_val - min_val)
        
        # Apply the weighted algorithm (40% income, 20% growth, 40% saturation)
        df['market_score'] = (
            (normalized.get('median_income', 0) * 0.40) +
            (normalized.get('population_growth', 0) * 0.20) +
            (normalized.get('saturation_index', 0) * 0.40)
        )
        return df
        
    def run_pipeline(self) -> pd.DataFrame:
        pass
