import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from database import DatabaseQueryCache
from filters import sidebar_filters
from charts import score_over_time, horizontal_bar
from queries import overview_query, dimension_query

@st.cache_resource
def get_db() -> DatabaseQueryCache:
    return DatabaseQueryCache(max_cache_age_minutes=15)

try:
    db = get_db()
except ValueError as e:
    st.error(str(e))
    st.stop()

st.title("Executive Overview")

params = sidebar_filters(db, key_prefix="overview", show_framework=True)

try:
    df_overview = db.query(overview_query(params), params)
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if df_overview.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

st.plotly_chart(score_over_time(df_overview))

col_left, col_right = st.columns(2)

try:
    df_bu = db.query(dimension_query("business_unit", params), params)
    with col_left:
        st.plotly_chart(
            horizontal_bar(df_bu, "business_unit", "Latest Score by Business Unit"),
        )
except Exception as e:
    with col_left:
        st.error(f"Could not load business unit data: {e}")

try:
    df_domain = db.query(dimension_query("domain", params), params)
    with col_right:
        st.plotly_chart(
            horizontal_bar(df_domain, "domain", "Latest Score by Cyber Domain"),
        )
except Exception as e:
    with col_right:
        st.error(f"Could not load domain data: {e}")
