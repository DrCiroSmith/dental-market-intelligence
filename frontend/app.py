import streamlit as st
import requests
import pandas as pd
import folium
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Dental Intel Pro", page_icon="🦷", layout="wide")

# CSS Fix for Dark Mode Visibility & Table Styling
st.markdown("""
    <style>
    /* Force high contrast for metrics and text */
    [data-testid="stMetricValue"] { color: #28a745 !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #555 !important; font-size: 1.1rem; }
    .main { background-color: transparent; }
    
    /* Custom Table Styling for Dark Mode */
    table { width: 100%; border-collapse: collapse; color: inherit; }
    th { background-color: #f1f3f5; color: #333; text-align: left; padding: 10px; }
    td { padding: 10px; border-bottom: 1px solid #dee2e6; }
    tr:nth-child(even) { background-color: rgba(127,127,127,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- Logic ---
@st.cache_data
def get_market_data(zip_code):
    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&taxonomy_description=Dentist&postal_code={zip_code}&limit=100"
    try:
        return requests.get(url).json().get('results', [])
    except: return []

@st.cache_data
def get_coords(zip_code):
    try:
        loc = Nominatim(user_agent="roi_intel").geocode(f"{zip_code}, USA")
        return [loc.latitude, loc.longitude] if loc else [25.8195, -80.3553]
    except: return [25.8195, -80.3553]

# --- UI ---
st.title("🦷 ROI Intel Pro v2.1")
target_zip = st.sidebar.text_input("📍 Target ZIP", value="33178")
revenue = st.sidebar.number_input("Annual Revenue ($)", value=2000000)
ebitda_val = st.sidebar.number_input("Current EBITDA ($)", value=525000)
practice_type = st.sidebar.selectbox("Market Category", ["solo_gp", "small_group", "specialty"])

tab1, tab2 = st.tabs(["📊 Arbitrage Engine", "🗺️ Market Map"])

with tab1:
    payload = {"net_income": ebitda_val, "interest": 0, "taxes": 0, "depreciation": 0, "add_backs": 0, "practice_type": practice_type}
    try:
        res = requests.post("http://127.0.0.1:8000/api/v1/valuate", json=payload).json()
        val = res['valuation_range']['typical_value']
        exit_val = ebitda_val * 12.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Value", f"${val:,.0f}")
        c2.metric("DSO Exit Potential", f"${exit_val:,.0f}")
        c3.metric("Arbitrage Gap", f"${exit_val - val:,.0f}")
        st.success(f"Market analysis for {target_zip} complete.")
    except: st.error("Backend offline.")

with tab2:
    providers = get_market_data(target_zip)
    coords = get_coords(target_zip)
    m = folium.Map(location=coords, zoom_start=13)
    components.html(m._repr_html_(), height=400)
    
    # Render table as HTML for dark mode compatibility
    p_df = pd.DataFrame([{"Name": f"{p['basic'].get('first_name','')} {p['basic'].get('last_name','')}", "Credential": p['basic'].get('credential','DDS')} for p in providers])
    st.markdown(p_df.to_html(index=False), unsafe_allow_html=True)

