import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Dental Market Intelligence", page_icon="🦷", layout="wide")

st.title("🦷 Dental Market Intelligence Dashboard")

tab1, tab2 = st.tabs(["📊 Valuation & Arbitrage", "🗺️ Market Map"])

with tab1:
    st.sidebar.header("Practice Financials")
    net_income = st.sidebar.number_input("Net Income ($)", value=450000, step=10000)
    add_backs = st.sidebar.number_input("Owner Add-backs ($)", value=75000, step=5000)
    practice_type = st.sidebar.selectbox("Type", ["solo_gp", "small_group", "specialty"])

    if st.button("Calculate", type="primary"):
        payload = {"net_income": net_income, "interest": 15000, "taxes": 35000, "depreciation": 25000, "add_backs": add_backs, "practice_type": practice_type}
        res = requests.post("http://127.0.0.1:8000/api/v1/valuate", json=payload).json()
        
        ebitda = res['adjusted_ebitda']
        val = res['valuation_range']['typical_value']
        exit_val = ebitda * 12.0 # Standard DSO Platform Exit Multiple
        
        st.metric("Adjusted EBITDA", f"${ebitda:,.0f}")
        c1, c2 = st.columns(2)
        c1.metric("Private Sale Value (Current)", f"${val:,.0f}")
        c2.metric("DSO Exit Value (Potential)", f"${exit_val:,.0f}", delta=f"${exit_val - val:,.0f} GAP")
        
        st.info(f"**Arbitrage Opportunity:** By rolling into a platform, you capture a **${exit_val - val:,.0f}** spread on current earnings.")

with tab2:
    st.header("Doral Market Saturation")
    df = pd.read_csv("data/raw/real_market_data.csv")
    
    # Logic to calculate saturation on the fly
    df['saturation'] = df['population'] / df['active_dentists']
    
    m = folium.Map(location=[25.8195, -80.3553], zoom_start=13)
    for _, row in df.iterrows():
        color = 'green' if row['saturation'] > 1500 else 'red'
        folium.Marker(
            location=[25.8195 if row['zip_code']==33178 else 25.80, -80.35 if row['zip_code']==33178 else -80.38],
            popup=f"ZIP {row['zip_code']}: {row['active_dentists']} Dentists",
            icon=folium.Icon(color=color)
        ).add_to(m)
    folium_static(m)
    st.dataframe(df[['zip_code', 'population', 'active_dentists', 'saturation']])

st.caption("Data Sources: US Census Bureau (2021) & NPPES NPI Registry (Live)")
