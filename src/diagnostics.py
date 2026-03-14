import os
import requests
import pandas as pd

def run_audit():
    print("🦷 --- DENTAL MARKET DASHBOARD: PROJECT HEALTH AUDIT ---")
    
    # 1. Server Status
    try:
        requests.get("http://127.0.0.1:8000/health")
        print("✅ Backend API: Operational")
    except:
        print("❌ Backend API: Offline or Unreachable")

    # 2. Data Health
    data_path = "data/raw/real_market_data.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"✅ Data Health: Found {len(df)} records in market dataset.")
    else:
        print("❌ Data Health: Market data file missing.")

    # 3. UX/UI & Performance Analysis
    print("\n💡 --- UX/UI AUDIT & RECOMMENDATIONS ---")
    with open("frontend/app.py", "r") as f:
        code = f.read()
        
    if "@st.cache" not in code:
        print("- [FIX] PERFORMANCE: You are not using @st.cache_data. Large NPI searches will feel slow.")
    if "st.columns" in code and "sidebar" not in code:
        print("- [UX] LAYOUT: Good use of columns, but ensure they stack well on mobile.")
    if "st.table" in code:
        print("- [UX] Bypassing PyArrow with st.table is a solid mobile fix, but consider custom CSS for 'zebra' rows to improve readability.")
    
    print("- [UI] SUGGESTION: Add a 'Download CSV' button for your NPI search results.")
    print("- [UI] SUGGESTION: Implement a 'Dark Mode' toggle in settings for late-night deal analysis.")

if __name__ == "__main__":
    run_audit()
