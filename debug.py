# debug.py - A simple script to find the error.
import streamlit as st
import requests
import traceback

URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
st.title("Project AURA - Debug Mode")
st.write("This page will test the data connection step-by-step.")

try:
    st.header("Step 1: Connection")
    response = requests.get(URL, timeout=15)
    response.raise_for_status()
    st.success("✅ Connection to NOAA server was successful.")
    print("DEBUG LOG: Connection OK.")

    st.header("Step 2: Read Data")
    data = response.json()
    st.success("✅ Data was received and is valid JSON.")
    print("DEBUG LOG: JSON parsing OK.")

    st.header("Step 3: Check Data Structure")
    # The data should be a list, where the first item is the header row
    header = data[0]
    st.write(f"Found header row: `{header}`")
    print(f"DEBUG LOG: Header is {header}")

    st.header("Step 4: Find the 'kp' Column")
    # We need to find the position of the 'kp' column
    if 'kp' in header:
        kp_column_index = header.index('kp')
        st.success(f"✅ Found the 'kp' column at position {kp_column_index}.")
        print(f"DEBUG LOG: 'kp' column found at index {kp_column_index}.")
    else:
        st.error(f"CRITICAL ERROR: Could not find the 'kp' column in the header!")
        raise KeyError("Column 'kp' not found in header")

    st.header("Step 5: Get Latest Data Row")
    # We will iterate backwards to find the last row with a valid number
    latest_kp_value = None
    for row in reversed(data[1:]):
        try:
            # Get the value from the correct column position
            value_from_row = row[kp_column_index]
            # Try to convert it to a number. This will fail if it's text.
            numeric_value = int(float(value_from_row))
            latest_kp_value = numeric_value
            st.success(f"✅ Found latest valid Kp value: {latest_kp_value}")
            print(f"DEBUG LOG: Found latest valid Kp value: {latest_kp_value}")
            break # Stop as soon as we find the first valid one from the end
        except (ValueError, TypeError):
            # This row doesn't contain a valid number, so we skip it
            continue

    if latest_kp_value is None:
        st.error("CRITICAL ERROR: Could not find any valid numeric Kp value in the data file.")
    else:
        st.header("FINAL RESULT")
        st.metric(label="Live Planetary K-index", value=f"Kp {latest_kp_value}")

except Exception as e:
    st.error("A critical error occurred during the process.")
    # This will print the full, detailed error right on the web page
    st.exception(e)
    # Also print it to the black command window
    print("\n--- A CRITICAL ERROR OCCURRED ---")
    traceback.print_exc()