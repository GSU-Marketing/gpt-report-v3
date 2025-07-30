# app.py (main entry point)

import streamlit as st
import uuid
import pandas as pd
from data_loaders import (
    load_data_from_gdrive,
    preprocess_timestamps,
    get_filtered_data
)
from chat_helpers import ask_gpt, get_compressed_csv

st.set_page_config(page_title="GSU Grad GPT Dashboard", layout="wide")

# Branding
st.image("logo.png", width=160)
st.markdown("## GPT-Powered Graduate-Marketing Data Explorer", unsafe_allow_html=True)

# Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.success("👈 Use the sidebar to explore the dashboard pages.")

# Load data once
if "df" not in st.session_state:
    try:
        st.sidebar.subheader("📂 Upload or Use Default")
        dev_key = st.sidebar.text_input("🔐 Dev Key (Optional)", type="password")
        uploaded_file = st.sidebar.file_uploader("Upload your data file", type=["xlsx", "parquet"])

        if uploaded_file and dev_key == st.secrets.get("DEV_KEY", ""):
            if uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_parquet(uploaded_file)
            st.sidebar.success("✅ Using uploaded file.")
        elif "gdrive" in st.secrets:
            df = load_data_from_gdrive()
            st.sidebar.caption("🔐 Data Source: Private Google Drive")
        else:
            st.error("🚨 No data source available.")
            st.stop()

        df = preprocess_timestamps(df)
        st.session_state.df = df

    except Exception as load_error:
        st.error("🚨 Failed to load data.")
        st.exception(load_error)
        st.stop()

# Data filters – make them available to all pages
df = st.session_state.df
st.sidebar.subheader("🔎 Filter Data")

programs = ["All"] + sorted(df['Applications Applied Program'].dropna().astype(str).str.strip().unique())
statuses = ["All"] + sorted(df['Person Status'].dropna().astype(str).str.strip().unique())
terms = ["All"] + sorted(df['Applications Applied Term'].dropna().astype(str).str.strip().unique())

selected_program = st.sidebar.selectbox("Program:", programs)
selected_status = st.sidebar.selectbox("Status:", statuses)
selected_term = st.sidebar.selectbox("Term:", terms)

filtered_df = get_filtered_data(df, selected_program, selected_status, selected_term)

# Date filter
ping_dates = pd.to_datetime(filtered_df["Ping Timestamp"], errors="coerce").dropna()
data_min, data_max = ping_dates.min(), ping_dates.max()
selected_dates = st.sidebar.date_input("📅 Date Range", (data_min.date(), data_max.date()))

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start, end = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
    filtered_df = filtered_df[(ping_dates >= start) & (ping_dates <= end)]
    st.sidebar.caption(f"📆 Showing data from **{start.date()}** to **{end.date()}**")

st.session_state.filtered_df = filtered_df

# GPT Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Ask a question about your data")
user_question = st.sidebar.text_area("What would you like to know?", height=100)

if user_question:
    with st.spinner("Asking AI..."):
        data_sample = get_compressed_csv(filtered_df)
        answer = ask_gpt(
            prompt=f"Here is the data:\n\n{data_sample}\n\nQuestion: {user_question}",
            system_prompt="You are a data analyst assistant that answers questions about CSV-style data."
        )
        if answer:
            st.sidebar.success("✅ Answer ready")
            st.sidebar.write(answer)
