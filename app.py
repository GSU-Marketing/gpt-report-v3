# app.py
import streamlit as st
import uuid
import pandas as pd

from data_loaders import load_data_from_gdrive, preprocess_timestamps
from chat_helpers import ask_gpt, get_compressed_csv

st.set_page_config(page_title="GSU Grad GPT Dashboard", layout="wide")

st.image("logo.png", width=160)
st.markdown("## Welcome to the GPT-Powered Graduate-Marketing Explorer")
st.success("👈 Use the sidebar to navigate through the dashboard pages.")

# Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# GPT Sidebar
st.sidebar.subheader("💬 Ask a question about your data")
user_question = st.sidebar.text_area("What would you like to know?", height=100)

if user_question:
    with st.spinner("Asking AI..."):
        try:
            df = load_data_from_gdrive()
            df = preprocess_timestamps(df)
            data_sample = get_compressed_csv(df.head(300))  # Trimmed for token efficiency
            answer = ask_gpt(
                prompt=f"Here is the data:\n\n{data_sample}\n\nQuestion: {user_question}",
                system_prompt="You are a data analyst assistant that answers questions about CSV-style data."
            )
            st.sidebar.success("✅ Answer ready")
            st.sidebar.write(answer)
        except Exception as e:
            st.sidebar.error("⚠️ Unable to load data or contact GPT.")
            st.sidebar.exception(e)
