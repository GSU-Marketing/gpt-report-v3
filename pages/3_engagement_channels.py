import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Engagement", layout="wide")
st.title("📡 Engagement & Channels")

df = st.session_state.get("filtered_df", pd.DataFrame())
gsu_colors = st.session_state.get("gsu_colors", ["#0039A6", "#0078D7", "#00B0F0"])

if df.empty:
    st.warning("No data loaded or filtered. Please return to Home and check your filters.")
    st.stop()

for col in ["Ping UTM Source", "Ping UTM Medium", "Ping UTM Campaign"]:
    if col in df.columns:
        data = df[col].dropna().astype(str).str.strip()
        data = data[data.str.lower() != "nan"]
        if not data.empty:
            if "Source" in col:
                fig = px.pie(data_frame=data.value_counts().reset_index(), names='index', values=col, title=col)
            else:
                fig = px.bar(data_frame=data.value_counts().reset_index(), x='index', y=col, title=col)
            st.plotly_chart(fig, use_container_width=True)

if "Ping Timestamp" in df.columns:
    df["Hour"] = pd.to_datetime(df["Ping Timestamp"], errors='coerce').dt.hour
    fig = px.histogram(df.dropna(subset=["Hour"]), x="Hour", nbins=24,
                       title="Activity by Hour of Day", color_discrete_sequence=gsu_colors)
    st.plotly_chart(fig, use_container_width=True)
