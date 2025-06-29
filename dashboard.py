# dashboard.py (Final Robust Version)
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Project AURA Sentinel",
    page_icon="🛰️",
    layout="wide"
)

# --- Data Fetching Functions ---
URL_KP_INDEX = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
URL_SOLAR_WIND = "https://services.swpc.noaa.gov/products/ace-real-time-solar-wind.json"

@st.cache_data(ttl=900) # Cache data for 15 minutes
def get_data():
    """Fetches all data and returns it in a dictionary."""
    data = {'kp_index': None, 'wind_speed': None, 'bz_gsm': None, 'timestamp': datetime.now()}
    
    # --- NEW: More robust Kp-index fetching ---
    try:
        kp_response = requests.get(URL_KP_INDEX).json()[1:]
        kp_df = pd.DataFrame(kp_response, columns=['valid_utc', 'observed_kp', 'kp_forecast', 'kp_noise'])
        
        # Iterate backwards to find the most recent valid forecast
        for index, row in kp_df.iloc[::-1].iterrows():
            try:
                # Try to convert the forecast to a number
                latest_kp = int(row['kp_forecast'])
                data['kp_index'] = latest_kp
                break # Stop as soon as we find a valid number
            except (ValueError, TypeError):
                # If it fails (e.g., it's the word "predicted"), just continue to the next row
                continue
                
    except Exception as e:
        # If the whole request fails, we'll see this error
        st.error(f"Error fetching Kp-index data: {e}")

    # --- NEW: More robust Solar Wind fetching ---
    try:
        wind_response = requests.get(URL_SOLAR_WIND).json()[1:]
        wind_df = pd.DataFrame(wind_response, columns=['time_tag', 'density', 'speed', 'temperature', 'bt', 'bz_gsm'])
        latest_wind = wind_df.iloc[-1]
        data['wind_speed'] = float(latest_wind['speed'])
        data['bz_gsm'] = float(latest_wind['bz_gsm'])
    except Exception as e:
        st.error(f"Error fetching Solar Wind data: {e}")
        
    return data

# --- Main Dashboard Page ---
st.title(f"🛰️ Project AURA Sentinel")

data = get_data()
st.write(f"Last updated: {data.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')} CEST")

st.header("Geomagnetic & Solar Wind Status")

col1, col2, col3 = st.columns(3)

# --- NEW: Display metrics only if data is available ---

# Kp-Index Metric
kp_index = data.get('kp_index')
if kp_index is not None:
    kp_help = "Planetary K-index. A measure of geomagnetic storm activity. 5 or higher indicates a geomagnetic storm."
    col1.metric(label="Planetary K-index", value=f"Kp {kp_index}", delta_color="inverse", help=kp_help)
else:
    col1.metric(label="Planetary K-index", value="N/A", delta_color="off")

# Solar Wind Speed Metric
wind_speed = data.get('wind_speed')
if wind_speed is not None:
    wind_help = "Speed of the plasma flowing from the sun."
    col2.metric(label="Solar Wind Speed", value=f"{wind_speed:.0f} km/s", help=wind_help)
else:
    col2.metric(label="Solar Wind Speed", value="N/A", delta_color="off")

# IMF Bz Metric
bz_gsm = data.get('bz_gsm')
if bz_gsm is not None:
    bz_delta = "Northward" if bz_gsm >= 0 else "Southward"
    bz_help = "Interplanetary Magnetic Field (IMF) Bz component. A strong southward Bz (negative value) can lead to auroral activity."
    col3.metric(label="IMF Bz Component", value=f"{bz_gsm:.1f} nT", delta=bz_delta, delta_color="off", help=bz_help)
else:
    col3.metric(label="IMF Bz Component", value="N/A", delta_color="off")

# --- Raw Data ---
with st.expander("Show Raw Data Tables"):
    st.write("Note: This data is cached and refreshes every 15 minutes.")
    st.subheader("Geomagnetic Forecast")
    try:
        st.dataframe(pd.read_json(URL_KP_INDEX).iloc[1:])
    except Exception as e:
        st.warning("Could not load Geomagnetic Forecast table.")
    
    st.subheader("Real-time Solar Wind")
    try:
        st.dataframe(pd.read_json(URL_SOLAR_WIND).iloc[1:])
    except Exception as e:
        st.warning("Could not load Solar Wind table.")