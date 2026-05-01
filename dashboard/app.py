import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="Continuous Control Monitoring",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"]::before {
        content: "Continuous Compliance Monitoring";
        display: block;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 1.5rem 1rem 0.75rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pg = st.navigation([
    st.Page("pages/1_Overview.py", title="Overview"),
    st.Page("pages/2_Metrics.py", title="Metrics"),
    st.Page("pages/3_About.py", title="About"),
])
pg.run()
