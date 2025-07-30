import streamlit as st
import pandas as pd
from data_loaders import get_gsheet_client

st.set_page_config(page_title="Admin", layout="wide")
st.title("🔒 Admin Dashboard")

admin_key = st.text_input("Enter Admin Access Key", type="password")
if admin_key != st.secrets.get("ADMIN_KEY"):
    st.warning("Access denied.")
    st.stop()

try:
    sheet = get_gsheet_client().open("Visitor Logs").sheet1
    records = sheet.get_all_records()
    logs_df = pd.DataFrame(records)
    st.dataframe(logs_df)
    st.download_button("📥 Download Logs CSV", logs_df.to_csv(index=False), "visitor_logs.csv")
except Exception as e:
    st.error("❌ Failed to load visitor logs.")
    st.exception(e)
