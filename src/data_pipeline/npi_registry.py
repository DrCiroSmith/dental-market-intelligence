import requests
import pandas as pd
import os

def fetch_npi_dentist_counts():
    print("Querying NPPES NPI Registry for Doral dentists...")
    url = "https://npiregistry.cms.hhs.gov/api/?version=2.1"
    
    # Doral ZIPs: 33178, 33122, 33166
    zips = ["33178", "33122", "33166"]
    results = {}

    for z in zips:
        params = {
            "taxonomy_description": "Dentist",
            "postal_code": z,
            "limit": 200
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                count = response.json().get('result_count', 0)
                results[z] = count
            else:
                results[z] = 0
        except:
            results[z] = 0
            
    # Update our existing market data
    df = pd.read_csv("data/raw/real_market_data.csv")
    df['active_dentists'] = df['zip_code'].astype(str).map(results).fillna(df['active_dentists'])
    df.to_csv("data/raw/real_market_data.csv", index=False)
    print(f"Updated NPI counts: {results}")

if __name__ == "__main__":
    fetch_npi_dentist_counts()
