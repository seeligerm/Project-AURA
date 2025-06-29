# test_parsing.py
import requests
import pandas as pd
import json

URL_TO_TEST = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
print(f"--- Testing Data Structure for URL: {URL_TO_TEST} ---\n")

try:
    response = requests.get(URL_TO_TEST, timeout=15)
    response.raise_for_status()
    print("✅ STEP 1: Connection successful. Received a response from the server.")

    print("\n--- RAW TEXT RESPONSE (first 500 chars) ---")
    print(response.text[:500])
    print("------------------------------------------\n")

    print("✅ STEP 2: Attempting to parse response as JSON...")
    data = response.json()
    print("     ...Success! Response is valid JSON.")

    print(f"\nData is a {type(data)} with {len(data)} items.")
    if isinstance(data, list) and len(data) > 1:
        print("First row (Header):", data[0])
        print("Second row (First data point):", data[1])

    print("\n✅ STEP 3: Attempting to create pandas DataFrame...")
    # This is the logic from our dashboard script that is failing
    header = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=header)
    print("     ...Success! DataFrame created.")

    print("\n✅ STEP 4: Attempting to extract the last 'kp_index' value...")
    last_value_str = df['kp_index'].iloc[-1]
    last_value_int = int(last_value_str)
    print(f"     ...Success! Extracted value is: {last_value_int}")

    print("\n\n--- DIAGNOSTIC COMPLETE: Parsing logic appears to be correct. ---")

except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP ERROR: The server responded with an error code. {e}")
except json.JSONDecodeError as e:
    print(f"❌ JSON ERROR: The server response was not valid JSON. {e}")
except (KeyError, IndexError) as e:
    print(f"❌ PARSING ERROR: The JSON structure was not what we expected. Could not find the right keys or rows. Error: {e}")
except Exception as e:
    print(f"❌ AN UNKNOWN ERROR OCCURRED: {e}")