import streamlit as st
import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Dental Intel Pro", page_icon="🦷", layout="wide")

# Custom CSS for Mobile Responsive UI
st.markdown("""
    <style>
    .stMetric { background: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    .table-responsive { overflow-x: auto; }
    .gap-metric { color: #28a745; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- CACHING LOGIC ---
@st.cache_data
def get_market_data(zip_code):
    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&taxonomy_description=Dentist&postal_code={zip_code}&limit=100"
    try:
        res = requests.get(url).json()
        providers = res.get('results', [])
        return providers
    except:
        return []

@st.cache_data
def get_coords(zip_code):
    geolocator = Nominatim(user_agent="dental_intel_pro")
    location = geolocator.geocode(f"{zip_code}, USA")
    if location:
        return [location.latitude, location.longitude]
    return [25.8195, -80.3553] # Default to Doral

# --- SIDEBAR ---
st.sidebar.title("🦷 ROI Intel v2.0")
target_zip = st.sidebar.text_input("📍 Target ZIP Code", value="33178")
st.sidebar.markdown("---")
st.sidebar.header("💰 Financial Audit")
revenue = st.sidebar.number_input("Annual Revenue ($)", value=2000000)
ebitda_val = st.sidebar.number_input("Current EBITDA ($)", value=525000)
practice_type = st.sidebar.selectbox("Market Category", ["solo_gp", "small_group", "specialty"])

# --- MAIN ENGINE ---
tab1, tab2, tab3 = st.tabs(["📊 Arbitrage Engine", "🗺️ Density Map", "📋 Acquisition List"])

providers = get_market_data(target_zip)
coords = get_coords(target_zip)

with tab1:
    st.header(f"Valuation Audit: {target_zip}")
    # Call our Backend API
    payload = {"net_income": ebitda_val, "interest": 0, "taxes": 0, "depreciation": 0, "add_backs": 0, "practice_type": practice_type}
    try:
        api_res = requests.post("http://127.0.0.1:8000/api/v1/valuate", json=payload).json()
        val = api_res['valuation_range']['typical_value']
        exit_val = ebitda_val * 12.0 # 2026 Platform Multiple
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Multiple", "4.6x (Typical)")
        c2.metric("Market Valuation", f"${val:,.0f}")
        c3.metric("DSO Exit Potential", f"${exit_val:,.0f}", delta=f"${exit_val - val:,.0f} ARBITRAGE")
        
        st.success(f"💡 This practice has a **${exit_val - val:,.0f}** Arbitrage Gap. Consolidating this into a DSO platform instantly unlocks this value.")
    except:
        st.warning("Connect Backend API to see valuation data.")

with tab2:
    st.header(f"Heatmap: {target_zip} Density")
    m = folium.Map(location=coords, zoom_start=13, tiles='CartoDB positron')
    
    # Generate Heatmap based on dentist counts
    heat_data = [[coords[0], coords[1], 1] for _ in range(len(providers))]
    HeatMap(heat_data, radius=25).add_to(m)
    folium.Marker(coords, popup="Target Center", icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
    
    components.html(m._repr_html_(), height=500)
    st.caption(f"Brighter areas indicate higher dentist density in ZIP {target_zip}.")

with tab3:
    st.header("Potential Acquisition Targets")
    if providers:
        p_data = []
        for p in providers:
            p_data.append({
                "Name": f"{p['basic'].get('first_name', '')} {p['basic'].get('last_name', '')}",
                "Credential": p['basic'].get('credential', 'DDS/DMD'),
                "Gender": p['basic'].get('gender', 'U'),
                "Address": p['addresses'][0].get('address_1', 'N/A')
            })
        st.markdown(pd.DataFrame(p_data).to_html(index=False, classes='table table-striped'), unsafe_allow_html=True)
    else:
        st.write("No providers found in this ZIP.")

st.markdown("---")
st.caption("Dental Market Intelligence v2.0 | DrCiroSmith Edition")
