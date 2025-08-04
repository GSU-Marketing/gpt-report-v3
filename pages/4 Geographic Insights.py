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
import us
from streamlit_folium import st_folium
import folium

from geo_utils import enrich_geo_fields, get_geoip_reader
from data_loaders import load_us_states_geojson

def render(filtered_df, gsu_colors):
    st.subheader("🌍 Geographic Insights")

    reader = get_geoip_reader()
    geo_df = enrich_geo_fields(filtered_df.copy(), reader)
    us_states_geojson = load_us_states_geojson()
    valid_state_names = [f["properties"]["NAME"] for f in us_states_geojson["features"]]

    geo_df_all = geo_df.copy()
    geo_df_us = geo_df.copy()
    geo_df_us["region"] = geo_df_us["region"].apply(
        lambda x: us.states.lookup(str(x)).name if us.states.lookup(str(x)) else str(x)
    ).astype(str).str.strip()
    geo_df_us = geo_df_us[geo_df_us["region"].isin(valid_state_names)]

    if st.sidebar.checkbox("🔎 Show Unmatched Regions", value=False):
        unmatched = geo_df_all[~geo_df_all["region"].isin(valid_state_names)]
        if not unmatched.empty:
            st.warning("⚠️ The following regions don't match U.S. states in the GeoJSON:")
            st.dataframe(unmatched["region"].value_counts().reset_index().rename(columns={"index": "Unmatched", "region": "Count"}))

    non_ga_df = geo_df_us[geo_df_us["region"] != "Georgia"].copy()
    zip_counts_non_ga = (
        non_ga_df["Zip Code"]
        .astype(str).str.zfill(5).replace("nan", pd.NA).dropna()
        .value_counts().reset_index()
    )
    zip_counts_non_ga.columns = ["Zip Code", "Count"]
    non_ga_df["City_Region"] = non_ga_df["city"].fillna("") + ", " + non_ga_df["region"].fillna("")
    city_counts_non_ga = non_ga_df["City_Region"].value_counts().reset_index()
    city_counts_non_ga.columns = ["City, Region", "Count"]

    zip_counts = (
        geo_df_us["Zip Code"]
        .astype(str).str.zfill(5).replace("nan", pd.NA).dropna()
        .value_counts().reset_index()
    )
    zip_counts.columns = ["Zip Code", "Count"]

    state_counts = geo_df_us["region"].value_counts().reset_index()
    state_counts.columns = ["region", "count"]

    m = folium.Map(location=[37.8, -96], zoom_start=4, tiles="cartodbpositron")
    folium.Choropleth(
        geo_data=us_states_geojson,
        name="choropleth",
        data=state_counts,
        columns=["region", "count"],
        key_on="feature.properties.NAME",
        fill_color="Blues",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Lead Count by U.S. State"
    ).add_to(m)
    folium.GeoJsonTooltip(fields=["NAME"]).add_to(folium.GeoJson(us_states_geojson))

    country_counts = geo_df_all["country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]
    fig_country = px.choropleth(
        country_counts,
        locations="Country",
        locationmode="country names",
        color="Count",
        title="Global Lead Distribution"
    )

    def normalize_country(country):
        country = str(country or "").strip().lower()
        return "USA" if country in {"united states", "us", "usa", "u.s.", "u.s.a.", "united states of america"} else "International"

    geo_df_all["is_domestic"] = geo_df_all["country"].apply(normalize_country)
    dom_counts = geo_df_all["is_domestic"].value_counts().reset_index()
    dom_counts.columns = ["Region", "Count"]
    fig_domestic = px.pie(dom_counts, names="Region", values="Count", title="USA vs International Leads")

    city_region_df = geo_df_all.copy()
    city_region_df["City_Region"] = city_region_df["city"].fillna("") + ", " + city_region_df["region"].fillna("")
    city_counts = city_region_df["City_Region"].value_counts().reset_index()
    city_counts.columns = ["City, Region", "Count"]

    zip_counts["Zip Code"] = zip_counts["Zip Code"].astype(str)
    zip_counts_non_ga["Zip Code"] = zip_counts_non_ga["Zip Code"].astype(str)
    city_counts["City, Region"] = city_counts["City, Region"].str.strip()
    city_counts_non_ga["City, Region"] = city_counts_non_ga["City, Region"].str.strip()

    zip_counts = zip_counts[zip_counts["Zip Code"].str.lower() != "none"]
    city_counts = city_counts[~city_counts["City, Region"].str.contains("None", case=False, na=False)]
    city_counts_non_ga = city_counts_non_ga[~city_counts_non_ga["City, Region"].str.contains("None", case=False, na=False)]
    zip_counts_non_ga = zip_counts_non_ga[zip_counts_non_ga["Zip Code"].str.lower() != "none"]

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📬 Top ZIP Codes", 
        "🗺 US States", 
        "🌐 Countries", 
        "🏙 Cities", 
        "🇺🇸 vs 🌍",
        "🌆 Cities Outside GA", 
        "📮 ZIPs Outside GA"
    ])

    with tab1:
        st.markdown("### 📬 Top ZIP Codes")
        st.dataframe(zip_counts.head(10))

    with tab2:
        st.markdown("### 🗺 Lead Density by U.S. State")
        st_folium(m, width=900, height=600)

    with tab3:
        st.markdown("### 🌐 Global Heatmap by Country")
        st.plotly_chart(fig_country)

    with tab4:
        st.markdown("### 🏙 Top 10 Cities by Engagement")
        st.dataframe(city_counts.head(10))

    with tab5:
        st.markdown("### 🇺🇸 Domestic vs 🌍 International")
        st.plotly_chart(fig_domestic)

    with tab6:
        st.markdown("### 🌆 Top Cities Outside Georgia")
        st.dataframe(city_counts_non_ga.head(10))

    with tab7:
        st.markdown("### 📮 Top ZIPs Outside Georgia")
        st.dataframe(zip_counts_non_ga.head(10))
