import streamlit as st
import uuid
from data_loaders import load_data_from_gdrive, preprocess_timestamps, get_filtered_data

st.set_page_config(page_title="PantherMetrics", layout="wide")

# Branding
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
        df = load_data_from_gdrive()
        df = preprocess_timestamps(df)

        # Default filter setup
        selected_program = "All"
        selected_status = "All"
        selected_term = "All"

        st.session_state["filtered_df"] = get_filtered_data(df, selected_program, selected_status, selected_term)

    except Exception as e:
        st.error("❌ Failed to load dataset.")
        st.exception(e)

st.success("👈 Use the sidebar to navigate the dashboard pages.")
