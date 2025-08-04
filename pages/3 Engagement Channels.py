import streamlit as st
import pandas as pd
import plotly.express as px
from chat_helpers import ask_gpt

def render(filtered_df, gsu_colors):
    st.subheader("📡 Engagement & Channels")

    if "Ping UTM Source" in filtered_df.columns:
        traffic_df = filtered_df[filtered_df["Ping UTM Source"].notna()]
        traffic_df = traffic_df[traffic_df["Ping UTM Source"].astype(str).str.strip().str.lower() != "nan"]
        traffic_df = traffic_df[traffic_df["Ping UTM Source"].astype(str).str.strip() != ""]
        if not traffic_df.empty:
            fig = px.pie(traffic_df, names="Ping UTM Source", title="Traffic Sources (UTM Source)")
            st.plotly_chart(fig, config={'displayModeBar': False})
        else:
            st.info("ℹ️ No UTM Source data to display.")

    if "Ping UTM Medium" in filtered_df.columns:
        medium_df = filtered_df[filtered_df["Ping UTM Medium"].notna()]
        medium_df = medium_df[medium_df["Ping UTM Medium"].astype(str).str.strip().str.lower() != "nan"]
        medium_df = medium_df[medium_df["Ping UTM Medium"].astype(str).str.strip() != ""]
        if not medium_df.empty:
            medium_counts = medium_df["Ping UTM Medium"].value_counts().reset_index()
            medium_counts.columns = ["UTM Medium", "Count"]
            fig = px.bar(medium_counts, x="UTM Medium", y="Count", title="Traffic by UTM Medium",
                         color_discrete_sequence=gsu_colors)
            st.plotly_chart(fig, config={'displayModeBar': False})
        else:
            st.info("ℹ️ No UTM Medium data to display.")

    if "Ping UTM Campaign" in filtered_df.columns:
        campaign_df = filtered_df[filtered_df["Ping UTM Campaign"].notna()]
        campaign_df = campaign_df[campaign_df["Ping UTM Campaign"].astype(str).str.strip().str.lower() != "nan"]
        campaign_df = campaign_df[campaign_df["Ping UTM Campaign"].astype(str).str.strip() != ""]
        if not campaign_df.empty:
            campaign_counts = campaign_df["Ping UTM Campaign"].value_counts().reset_index()
            campaign_counts.columns = ["Campaign", "Count"]
            fig = px.bar(campaign_counts, x="Campaign", y="Count", title="Traffic by UTM Campaign",
                         color_discrete_sequence=gsu_colors)
            st.plotly_chart(fig, config={'displayModeBar': False})
        else:
            st.info("ℹ️ No UTM Campaign data to display.")

    if "Ping Timestamp" in filtered_df.columns:
        filtered_df["Hour"] = pd.to_datetime(filtered_df["Ping Timestamp"], errors='coerce').dt.hour
        fig = px.histogram(filtered_df.dropna(subset=["Hour"]), x="Hour", nbins=24,
                           title="Activity by Hour of Day", color_discrete_sequence=gsu_colors)
        st.plotly_chart(fig, config={'displayModeBar': False})

    if "Applications Created Date" in filtered_df.columns:
        created_counts = filtered_df.dropna(subset=["Applications Created Date"])
        created_counts = created_counts[created_counts["Applications Created Date"].astype(str).str.lower() != "nan"]
        if not created_counts.empty:
            fig = px.histogram(created_counts, x="Applications Created Date",
                               title="Applications Created Over Time",
                               color_discrete_sequence=gsu_colors)
            st.plotly_chart(fig, config={'displayModeBar': False})

    if "Applications Submitted Date" in filtered_df.columns:
        submitted_counts = filtered_df.dropna(subset=["Applications Submitted Date"])
        submitted_counts = submitted_counts[submitted_counts["Applications Submitted Date"].astype(str).str.lower() != "nan"]
        if not submitted_counts.empty:
            fig = px.histogram(submitted_counts, x="Applications Submitted Date",
                               title="Applications Submitted Over Time",
                               color_discrete_sequence=gsu_colors)
            st.plotly_chart(fig, config={'displayModeBar': False})

    if st.sidebar.checkbox("🧠 Show Page Summary", value=False):
        st.markdown("### 🧠 Summary")
        with st.spinner("Summarizing Page 3..."):
            page_sample = filtered_df.head(300).to_csv(index=False)
            summary = ask_gpt(
                prompt=f"Summarize this marketing traffic data:\n\n{page_sample}",
                system_prompt="You are a data analyst summarizing UTM and engagement metrics."
            )
            if summary:
                st.info(summary)
