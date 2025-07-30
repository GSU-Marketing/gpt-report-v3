import streamlit as st
import os
import requests
import pandas as pd

LOCAL_MMDB_PATH = "/tmp/GeoLite2-City.mmdb"

@st.cache_resource
def get_geoip_reader():
    import geoip2.database

    def download_large_file_from_drive(file_id, destination):
        session = requests.Session()
        URL = "https://docs.google.com/uc?export=download"
        response = session.get(URL, params={"id": file_id}, stream=True)
        token = None
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value
        if token:
            response = session.get(URL, params={"id": file_id, "confirm": token}, stream=True)
        with open(destination, "wb") as f:
            for chunk in response.iter_content(32768):
                if b"<html" in chunk[:100].lower():
                    raise ValueError("❌ ERROR: File is not a valid .mmdb binary.")
                f.write(chunk)

    if not os.path.exists(LOCAL_MMDB_PATH):
        with st.spinner("⬇️ Downloading GeoLite2-City.mmdb..."):
            download_large_file_from_drive("1_wuanXceHz-XUaXSMrIT-lBM7qWrCPqI", LOCAL_MMDB_PATH)

    return geoip2.database.Reader(LOCAL_MMDB_PATH)

def ip_to_geo(ip, reader):
    try:
        response = reader.city(ip)
        return {
            "Zip Code": response.postal.code,
            "city": response.city.name,
            "region": response.subdivisions.most_specific.name,
            "country": response.country.name
        }
    except:
        return {"Zip Code": None, "city": None, "region": None, "country": None}

@st.cache_data(show_spinner="🌍 Enriching Geo Fields...", show_time=True)
def enrich_geo_fields(df, reader):
    def enrich_row(row):
        geo = ip_to_geo(row.get("Ping IP Address", ""), reader)
        if pd.notna(row.get("Zip Code")) and str(row["Zip Code"]).strip():
            geo["Zip Code"] = row["Zip Code"]  # Preserve manual ZIPs
        return pd.Series(geo)

    enriched = df.apply(enrich_row, axis=1)
    for col in ["Zip Code", "city", "region", "country"]:
        df[col] = enriched[col]
    return df

def load_us_states_geojson():
    import json
    with open("us-states.json", "r") as f:
        return json.load(f)
