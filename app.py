import streamlit as st
import uuid

st.set_page_config(page_title="PantherMetrics", layout="wide")

# App Identity
st.image("logo.png", width=160)
st.markdown("## GPT-Powered Graduate-Marketing Data Explorer")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.success("👈 Use the sidebar to navigate the dashboard pages.")
