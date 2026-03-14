import requests
import pandas as pd
import os

def fetch_florida_zip_data():
    print("Fetching real demographic data from US Census API...")
    # US Census API endpoint for ACS 5-Year Estimates
    url = "https://api.census.gov/data/2021/acs/acs5"
    # B01003_001E = Population, B19013_001E = Median Household Income
    params = {
        "get": "NAME,B01003_001E,B19013_001E",
        "for": "zip code tabulation area:33178,33122,33166", # Doral ZIPs
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        
        # Clean and format the Census data
        df = df.rename(columns={
            'zip code tabulation area': 'zip_code',
            'B01003_001E': 'population',
            'B19013_001E': 'median_income'
        })
        
        # Add synthetic data for variables the Census doesn't track (Active Dentists & Growth)
        # (In Phase 2, we will pull this directly from the NPI registry)
        df['active_dentists'] = [45, 2, 20] 
        df['population_growth'] = [0.05, -0.02, 0.01]
        
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv("data/raw/real_market_data.csv", index=False)
        print("Success: Real Census data saved to data/raw/real_market_data.csv")
    else:
        print(f"Failed to fetch Census data: {response.text}")

if __name__ == "__main__":
    fetch_florida_zip_data()
