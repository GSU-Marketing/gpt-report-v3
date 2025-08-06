import streamlit as st
import uuid
import os

st.set_page_config(page_title="PantherMetrics", layout="wide")

st.write("✅ app.py loaded")

# Check secrets
try:
    st.write("🔐 GCP Client Email:", st.secrets["gcp"]["client_email"])
    st.write("📄 GDrive File ID:", st.secrets["gdrive"]["file_id"])
except Exception as e:
    st.error("❌ GCP or GDrive secrets missing or invalid.")
    st.exception(e)
    st.stop()

try:
    from data_loaders import load_data_from_gdrive, preprocess_timestamps, get_filtered_data
    st.write("✅ data_loaders imported")
except Exception as e:
    st.error("❌ Failed to import data_loaders")
    st.exception(e)
    st.stop()

# Branding
if os.path.exists("logo.png"):
    st.image("logo.png", width=160)

st.markdown("## GPT-Powered Graduate-Marketing Data Explorer")

# Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Color palette
st.session_state["gsu_colors"] = ['#0055CC', '#00A3AD', '#FDB913', '#C8102E']

# Load and cache data
if "filtered_df" not in st.session_state:
    try:
        st.write("📦 Loading data from Google Drive...")
        df = load_data_from_gdrive()
        df = preprocess_timestamps(df)
        st.write("✅ Data loaded and preprocessed")

        # Default filter setup
        selected_program = "All"
        selected_status = "All"
        selected_term = "All"

        st.session_state["filtered_df"] = get_filtered_data(df, selected_program, selected_status, selected_term)

    except Exception as e:
        st.error("❌ Failed to load dataset.")
        st.exception(e)

st.success("App booted successfully ✅")
