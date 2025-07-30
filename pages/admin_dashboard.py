import streamlit as st
import pandas as pd
from data_loaders import get_gsheet_client

def render():
    st.subheader("🔒 Admin Dashboard")
    admin_key = st.text_input("Enter Admin Access Key", type="password")
    if admin_key != st.secrets["ADMIN_KEY"]:
        st.warning("Access denied.")
        st.stop()

    st.success("Access granted. Welcome, Admin.")

    def get_visitor_logs():
        client = get_gsheet_client()
        sheet = client.open("Visitor Logs").sheet1
        records = sheet.get_all_records()
        return pd.DataFrame(records)

    try:
        logs_df = get_visitor_logs()
        st.dataframe(logs_df)
        st.download_button("📥 Download Logs CSV", logs_df.to_csv(index=False), "visitor_logs.csv")
    except Exception as e:
        st.error("❌ Failed to load visitor logs.")
        st.exception(e)