import streamlit as st
from database import DatabaseQueryCache


def sidebar_filters(
    db: DatabaseQueryCache,
    key_prefix: str,
    show_framework: bool = True,
) -> dict:
    """Render sidebar filters and return a params dict of selected values."""
    params: dict = {}

    try:
        bu_df = db.query(
            "SELECT DISTINCT business_unit FROM mrt_v2_summary WHERE is_latest IS true ORDER BY business_unit"
        )
        bu_options = [""] + list(bu_df["business_unit"])
    except Exception:
        bu_options = []

    try:
        team_df = db.query(
            "SELECT DISTINCT team FROM mrt_v2_summary WHERE is_latest IS true ORDER BY team"
        )
        team_options = [""] + list(team_df["team"])
    except Exception:
        team_options = []

    try:
        loc_df = db.query(
            "SELECT DISTINCT location FROM mrt_v2_summary WHERE is_latest IS true ORDER BY location"
        )
        loc_options = [""] + list(loc_df["location"])
    except Exception:
        loc_options = []

    st.sidebar.header("Filters")

    selected_bu = st.sidebar.selectbox(
        "Business Unit", bu_options, key=f"{key_prefix}_bu",
        format_func=lambda x: "All" if x == "" else x,
    )
    selected_team = st.sidebar.selectbox(
        "Team", team_options, key=f"{key_prefix}_team",
        format_func=lambda x: "All" if x == "" else x,
    )
    selected_loc = st.sidebar.selectbox(
        "Location", loc_options, key=f"{key_prefix}_loc",
        format_func=lambda x: "All" if x == "" else x,
    )

    if show_framework:
        try:
            fw_df = db.query("SELECT DISTINCT framework FROM mrt_v2_framework ORDER BY framework")
            fw_options = list(fw_df["framework"])
        except Exception:
            fw_options = ["CIS 8.1"]

        selected_fw = st.sidebar.selectbox(
            "Framework", fw_options, key=f"{key_prefix}_fw",
        )
        if selected_fw:
            params["framework"] = selected_fw

    if selected_bu:
        params["business_unit"] = selected_bu
    if selected_team:
        params["team"] = selected_team
    if selected_loc:
        params["location"] = selected_loc

    return params
