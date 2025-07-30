import streamlit as st
import pandas as pd
import gspread
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials

@st.cache_resource
def get_gsheet_client():
    creds_dict = dict(st.secrets["gcp"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

@st.cache_data(ttl=3600, show_spinner="📥 Loading Google Sheet...", show_time=True)
def load_google_sheet(sheet_name="STAGE 5"):
    client = get_gsheet_client()
    worksheet = client.open("2025-2026 Grad Marketing Data (Refreshed Weekly)").worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

@st.cache_data(ttl=3600, show_spinner="📥 Loading GDrive data...", show_time=True)
def load_data_from_gdrive():
    client = get_gsheet_client()
    sheet = client.open_by_key(st.secrets["gdrive"]["file_id"]).sheet1
    records = sheet.get_all_records()
    return pd.DataFrame(records)

@st.cache_data(ttl=3600, show_spinner="🌎 Loading US States GeoJSON...", show_time=True)
def load_us_states_geojson():
    file_id = "1hsUzy5HmhEa_s5vu3uUdpnps-hpbQ_WQ"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = requests.get(url)
    return json.loads(r.content)

@st.cache_data(show_spinner="⏳ Preprocessing timestamps...", show_time=True)
def preprocess_timestamps(df):
    for col in ["Ping Timestamp", "Applications Created Date", "Applications Submitted Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

@st.cache_data
def get_filtered_data(df, program, status, term):
    if program != "All":
        df = df[df['Applications Applied Program'] == program]
    if status != "All":
        df = df[df['Person Status'] == status]
    if term != "All":
        df = df[df['Applications Applied Term'] == term]
    return df