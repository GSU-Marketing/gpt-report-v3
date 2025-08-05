import streamlit as st
import uuid
from data_loaders import load_data_from_gdrive, preprocess_timestamps, get_filtered_data

def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "gsu_colors" not in st.session_state:
        st.session_state["gsu_colors"] = ['#0055CC', '#00A3AD', '#FDB913', '#C8102E']

    if "filtered_df" not in st.session_state:
        try:
            df = load_data_from_gdrive()
            df = preprocess_timestamps(df)
            st.session_state["filtered_df"] = get_filtered_data(df, "All", "All", "All")
        except Exception as e:
            st.error("❌ Failed to load dataset.")
            st.exception(e)