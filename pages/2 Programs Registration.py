import streamlit as st
import pandas as pd
import plotly.express as px

if "filtered_df" not in st.session_state or "gsu_colors" not in st.session_state:
    st.error("❌ Data not loaded. Please return to the home page to initialize data.")
    st.stop()

filtered_df = st.session_state["filtered_df"]
gsu_colors = st.session_state["gsu_colors"]

import streamlit as st
import pandas as pd
import plotly.express as px
from chat_helpers import ask_gpt

def render(filtered_df, gsu_colors):
    st.subheader("📊 Programs & Registration Hours")

    top_programs = (
        filtered_df['Applications Applied Program']
        .dropna()
        .astype(str)
        .loc[lambda x: (x.str.strip() != "") & (x.str.lower() != "nan")]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_programs.columns = ['Program', 'Count']

    fig = px.bar(top_programs, x='Count', y='Program', orientation='h', title="Top Applied Programs",
                 color_discrete_sequence=gsu_colors)
    st.plotly_chart(fig, config={'displayModeBar': False})

    reg_cols = [col for col in filtered_df.columns if "Registration Hours" in col]
    reg_df = filtered_df[reg_cols].copy()
    melted = reg_df.melt(var_name="Term", value_name="Hours").dropna()

    melted["Hours"] = pd.to_numeric(melted["Hours"], errors="coerce")
    melted = melted.dropna(subset=["Hours"])

    show_avg = st.sidebar.checkbox("Show Average Hours per Person", value=False)
    if show_avg:
        avg_df = melted.groupby("Term")["Hours"].mean().reset_index()
        fig = px.bar(avg_df, x="Term", y="Hours", title="Average Registration Hours by Term",
                     color_discrete_sequence=gsu_colors)
    else:
        sum_df = melted.groupby("Term")["Hours"].sum().reset_index()
        fig = px.bar(sum_df, x="Term", y="Hours", title="Total Registration Hours by Term",
                     color_discrete_sequence=gsu_colors)

    st.plotly_chart(fig, config={'displayModeBar': False})

    if st.sidebar.checkbox("🧠 Show Page Summary", value=False):
        st.markdown("### 🧠 Summary")
        with st.spinner("Summarizing Page 2..."):
            page_sample = filtered_df.head(300).to_csv(index=False)
            summary = ask_gpt(
                prompt=f"Summarize this data with attention to geographic and program details:\n\n{page_sample}",
                system_prompt="You are a data analyst summarizing geographic and program-related patterns."
            )
            if summary:
                st.info(summary)
