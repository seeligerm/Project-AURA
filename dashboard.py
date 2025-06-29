# dashboard.py (Final Version with Corrected Parsing Logic)
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Project AURA Sentinel", page_icon="🛰️", layout="wide")

# --- Data Sources ---
URL_KP_INDEX = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
URL_SOLAR_WIND = "https://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json"
URL_GOES_FLARE = "https://services.swpc.noaa.gov/products/goes-x-ray-flux-5-minute.json"
URL_SDO_IMAGE = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_HMIIC.jpg"

@st.cache_data(ttl=600) # Cache data for 10 minutes
def get_data():
    """Fetches all data and returns it in a dictionary."""
    data = {'kp_index': None, 'wind_speed': None, 'flare_class': None, 'flare_flux_series': None, 'timestamp': datetime.now()}

    try:
        kp_response = requests.get(URL_KP_INDEX).json()
        # THE FIX IS HERE: Use 'Kp' with a capital K to match the real header
        kp_df = pd.DataFrame(kp_response[1:], columns=kp_response[0])
        kp_df['Kp'] = pd.to_numeric(kp_df['Kp'], errors='coerce')
        kp_df.dropna(subset=['Kp'], inplace=True)
        data['kp_index'] = int(kp_df.iloc[-1]['Kp'])
    except Exception: st.warning("Could not retrieve live Kp-index data.")

    try:
        wind_response = requests.get(URL_SOLAR_WIND).json()
        wind_df = pd.DataFrame(wind_response[1:], columns=wind_response[0])
        wind_df['speed'] = pd.to_numeric(wind_df['speed'], errors='coerce')
        wind_df.dropna(subset=['speed'], inplace=True)
        data['wind_speed'] = wind_df.iloc[-1]['speed']
    except Exception: st.warning("Could not retrieve live Solar Wind data.")

    try:
        flare_response = requests.get(URL_GOES_FLARE).json()
        flare_df = pd.DataFrame(flare_response[1:], columns=flare_response[0])
        flare_df['flux'] = pd.to_numeric(flare_df['flux'], errors='coerce')
        flare_df.dropna(subset=['flux'], inplace=True)
        flare_df['time_tag'] = pd.to_datetime(flare_df['time_tag'])
        flare_df.set_index('time_tag', inplace=True)
        latest_flux = flare_df['flux'].iloc[-1]
        def classify_flare(flux):
            if flux < 1e-8: return f"A{(flux / 1e-9):.1f}"
            if flux < 1e-7: return f"B{(flux / 1e-8):.1f}"
            if flux < 1e-6: return f"C{(flux / 1e-7):.1f}"
            if flux < 1e-5: return f"M{(flux / 1e-6):.1f}"
            if flux >= 1e-5: return f"X{(flux / 1e-5):.1f}"
        data['flare_class'] = classify_flare(latest_flux)
        data['flare_flux_series'] = flare_df['flux']
    except Exception: st.warning("Could not retrieve live Solar Flare data.")

    return data

# --- Main Dashboard Page ---
st.title(f"🛰️ Project AURA Sentinel")
data = get_data()
st.write(f"Last updated: {data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')} CEST")

col1, col2 = st.columns([1, 2], gap="large") 

with col1:
    st.header("Live Sun")
    st.image(URL_SDO_IMAGE, caption="SDO/HMI Continuum")

with col2:
    st.header("Key Metrics")
    sub_col1, sub_col2, sub_col3 = st.columns(3)

    kp_val = data.get('kp_index')
    sub_col1.metric(label="Planetary K-index", value=f"Kp {kp_val}" if kp_val is not None else "N/A")

    wind_val = data.get('wind_speed')
    sub_col2.metric(label="Solar Wind Speed", value=f"{wind_val:.0f} km/s" if wind_val is not None else "N/A")

    flare_val = data.get('flare_class')
    sub_col3.metric(label="Max Flare Class (5m)", value=flare_val if flare_val is not None else "N/A")

    st.text("") 
    st.subheader("GOES X-Ray Flux (Last 2 Hours)")
    flare_series = data.get('flare_flux_series')
    if flare_series is not None and not flare_series.empty:
        st.line_chart(flare_series)
    else:
        st.warning("Flare activity chart is currently unavailable.")