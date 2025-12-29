import streamlit as st
import uuid
import os

st.set_page_config(page_title="PIPELINE DEVELOPER", layout="wide")

# Import modules
from data_loaders import load_data_from_gdrive, preprocess_timestamps, get_filtered_data

# Branding
if os.path.exists("logo.png"):
    st.image("logo.png", width=160)

st.markdown("# PIPELINE DEVELOPER RESEARCH LAB")
st.markdown("**Applied research, analytics, and AI tools for small businesses and growing organizations.**")

st.markdown("### Services")
st.markdown("""
- Market and product research (demand, competition, pricing)  
- Lead pipeline research (lists, segmentation, validation)  
- Data dashboards and analytics apps (cloud-based)  
- Custom GPT tools for internal workflows  
- Proposal-based research funding pilots  
""")

st.markdown("### Contact / Intake")
st.markdown("Request a proposal: **kulturemetrics.io/contact**  •  Email: **pipelinedeveloper.inc@gmail.com**")



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

# App ready
st.success("App booted successfully ✅")
