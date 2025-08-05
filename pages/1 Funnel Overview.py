import streamlit as st
from session_initializer import initialize_session
initialize_session()
import pandas as pd
import plotly.express as px

if "filtered_df" not in st.session_state or "gsu_colors" not in st.session_state:
    st.error("❌ Data not loaded. Please return to the home page to initialize data.")
    st.stop()

filtered_df = st.session_state["filtered_df"]
gsu_colors = st.session_state["gsu_colors"]

import streamlit as st
from session_initializer import initialize_session
initialize_session()
import pandas as pd
import plotly.express as px
from chat_helpers import ask_gpt, summarize_funnel_metrics

def render(filtered_df, gsu_colors):
    st.subheader("🪣 Funnel Overview")

    inquiries = len(filtered_df[filtered_df['Person Status'] == 'Inquiry'])
    applicants = len(filtered_df[filtered_df['Person Status'] == 'Applicant'])
    enrolled = len(filtered_df[filtered_df['Person Status'] == 'Enrolled'])
    stacked = st.sidebar.checkbox("📱 Mobile View", value=True)

    if stacked:
        st.metric("🧠 Inquiries", inquiries, help="Total number of inquiries", height=90)
        st.metric("📄 Applicants", applicants, help="Total number of applicants", height=90)
        st.metric("🎓 Enrolled", enrolled, help="Total number of enrollments", height=90)
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("🧠 Inquiries", inquiries, help="Total number of inquiries", height=90)
        col2.metric("📄 Applicants", applicants, help="Total number of applicants", height=90)
        col3.metric("🎓 Enrolled", enrolled, help="Total number of enrollments", height=90)

    funnel_data = pd.DataFrame({
        "Stage": ["Inquiry", "Applicant", "Enrolled"],
        "Count": [inquiries, applicants, enrolled]
    })
    funnel_fig = px.bar(funnel_data, x="Count", y="Stage", text="Count", color="Stage",
                        title="Lead Funnel", color_discrete_sequence=gsu_colors, orientation="h")
    funnel_fig.update_traces(textposition='outside')
    st.plotly_chart(funnel_fig, use_container_width=stacked, config={'displayModeBar': False})

    leads_over_time = filtered_df[filtered_df['Person Status'].isin(['Inquiry', 'Applicant', 'Enrolled'])]
    leads_over_time = leads_over_time.dropna(subset=["Ping Timestamp"])
    fig = px.histogram(leads_over_time, x="Ping Timestamp", color="Person Status", barmode="group",
                       title="Leads Over Time", color_discrete_sequence=gsu_colors)
    st.plotly_chart(fig, use_container_width=stacked, config={'displayModeBar': False})

    df_term = filtered_df.copy()
    df_term["Term"] = df_term["Applications Applied Term"].combine_first(df_term.get("Person Inquiry Term"))
    df_term = df_term[df_term["Person Status"].isin(["Inquiry", "Applicant", "Enrolled"])]
    df_term = df_term[df_term["Term"].notna() & (df_term["Term"].astype(str).str.strip().str.lower() != "nan")]
    term_counts = df_term.groupby(["Term", "Person Status"]).size().reset_index(name="Count")

    fig = px.bar(term_counts, x="Term", y="Count", color="Person Status", barmode="group",
                 title="Leads by Term", color_discrete_sequence=gsu_colors)
    st.plotly_chart(fig, use_container_width=stacked, config={'displayModeBar': False})

    if st.sidebar.checkbox("🧠 Show Page Summary", value=False):
        st.markdown("### 🧠 Summary")
        with st.spinner("Summarizing Page 1..."):
            summary_input = summarize_funnel_metrics(filtered_df)
            summary = ask_gpt(
                prompt=f"Provide a funnel drop-off summary using this data:\n\n{summary_input}",
                system_prompt="You are a data analyst providing a brief summary of the data."
            )
            if summary:
                st.info(summary)
