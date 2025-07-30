import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium
from geo_utils import get_geoip_reader, enrich_geo_fields, load_us_states_geojson
import us

st.set_page_config(page_title="Geographic Insights", layout="wide")
st.title("🌍 Geographic Insights")

df = st.session_state.get("filtered_df", pd.DataFrame())
gsu_colors = st.session_state.get("gsu_colors", ["#0039A6", "#0078D7", "#00B0F0"])

if df.empty:
    st.warning("No data loaded or filtered.")
    st.stop()

reader = get_geoip_reader()
geo_df = enrich_geo_fields(df.copy(), reader)
geo_df["region"] = geo_df["region"].apply(lambda x: us.states.lookup(str(x)).name if us.states.lookup(str(x)) else x).astype(str).str.strip()

us_states_geojson = load_us_states_geojson()
valid_states = [f["properties"]["NAME"] for f in us_states_geojson["features"]]
geo_df_us = geo_df[geo_df["region"].isin(valid_states)]

state_counts = geo_df_us["region"].value_counts().reset_index()
state_counts.columns = ["region", "count"]

m = folium.Map(location=[37.8, -96], zoom_start=4, tiles="cartodbpositron")
folium.Choropleth(
    geo_data=us_states_geojson,
    data=state_counts,
    columns=["region", "count"],
    key_on="feature.properties.NAME",
    fill_color="Blues",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Lead Count by U.S. State"
).add_to(m)
st_folium(m, width=900, height=600)
