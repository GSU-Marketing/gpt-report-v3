import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Programs & Hours", layout="wide")
st.title("📊 Programs & Registration Hours")

df = st.session_state.get("filtered_df", pd.DataFrame())
gsu_colors = st.session_state.get("gsu_colors", ["#0039A6", "#0078D7", "#00B0F0"])

if df.empty:
    st.warning("No data loaded or filtered. Please return to Home and check your filters.")
    st.stop()

top_programs = df['Applications Applied Program'].dropna().astype(str).value_counts().head(10).reset_index()
top_programs.columns = ['Program', 'Count']
fig = px.bar(top_programs, x='Count', y='Program', orientation='h',
             title="Top Applied Programs", color_discrete_sequence=gsu_colors)
st.plotly_chart(fig, use_container_width=True)

reg_cols = [col for col in df.columns if "Registration Hours" in col]
melted = df[reg_cols].melt(var_name="Term", value_name="Hours").dropna()
melted["Hours"] = pd.to_numeric(melted["Hours"], errors="coerce").dropna()

if st.sidebar.checkbox("Show Average Hours per Person", value=False):
    agg_df = melted.groupby("Term")["Hours"].mean().reset_index()
    fig = px.bar(agg_df, x="Term", y="Hours", title="Average Registration Hours by Term", color_discrete_sequence=gsu_colors)
else:
    agg_df = melted.groupby("Term")["Hours"].sum().reset_index()
    fig = px.bar(agg_df, x="Term", y="Hours", title="Total Registration Hours by Term", color_discrete_sequence=gsu_colors)
st.plotly_chart(fig, use_container_width=True)
