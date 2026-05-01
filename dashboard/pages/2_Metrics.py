import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

load_dotenv()

from database import DatabaseQueryCache
from filters import sidebar_filters
from queries import metrics_query, metric_detail_query, detail_query
from charts import score_over_time
from colours import get_rag_colours
import plotly.graph_objects as go

@st.cache_resource
def get_db() -> DatabaseQueryCache:
    return DatabaseQueryCache(max_cache_age_minutes=15)


try:
    db = get_db()
except ValueError as e:
    st.error(str(e))
    st.stop()


def _rag_colour(rag: str) -> str:
    return get_rag_colours().get(rag, "")


def _render_metric_detail(metric_id: str, params: dict) -> None:
    try:
        meta = db.query(
            "SELECT title, description FROM mrt_v2_metric_library WHERE is_latest IS true AND metric_id = :metric_id",
            {"metric_id": metric_id},
        )
    except Exception as e:
        st.error(f"Could not load metric metadata: {e}")
        return

    if not meta.empty:
        st.subheader(f"{metric_id} — {meta.iloc[0]['title']}")
        st.write(meta.iloc[0]["description"])
    else:
        st.subheader(f"{metric_id} — No description found")

    detail_params = {**params, "metric_id": metric_id}

    try:
        df_score = db.query(metric_detail_query(detail_params), detail_params)
    except Exception as e:
        st.error(f"Could not load metric score data: {e}")
        df_score = pd.DataFrame()

    if not df_score.empty:
        st.plotly_chart(
            score_over_time(df_score, title="Individual metric score over time"),
        )

    st.subheader("Detail")
    try:
        df_detail = db.query(detail_query(detail_params), detail_params)
    except Exception as e:
        st.error(f"Could not load detail data: {e}")
        return

    if df_detail.empty:
        st.info("No detail records found.")
        return

    df_detail = df_detail.copy()
    df_detail["rag"] = df_detail["compliance"].apply(
        lambda x: "red" if x == 0 else ("green" if x == 1 else "amber")
    )
    df_detail["compliance"] = df_detail["compliance"].apply(
        lambda x: str(int(x)) if x in [0, 1] else f"{float(x):.1f}"
    )

    def _row_style(row: pd.Series) -> list[str]:
        rag = row.get("rag", "")
        colour = _rag_colour(rag)
        text = "#ffffff" if rag in ("red", "green") else "#000000"
        styles = [""] * len(row)
        compliance_idx = list(row.index).index("compliance")
        styles[compliance_idx] = f"background-color: {colour}; color: {text}"
        return styles

    display_cols = ["upload_date", "resource", "owner", "detail", "compliance"]
    styled = (
        df_detail[display_cols + ["rag"]]
        .style.apply(_row_style, axis=1)
        .hide(axis="index")
    )
    st.dataframe(styled, column_config={"rag": None}, height=600)

    if st.button("← Back to Metrics"):
        st.query_params.clear()
        st.rerun()


# Check if we're in metric-detail mode
qp = st.query_params
selected_metric = qp.get("metric_id")

params = sidebar_filters(db, key_prefix="metrics", show_framework=True)

if selected_metric:
    _render_metric_detail(selected_metric, params)
else:
    st.title("Metrics")

    try:
        df = db.query(metrics_query(params), params)
    except Exception as e:
        st.error(f"Database error: {e}")
        st.stop()

    if df.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.sort_values(by="score", ascending=True)
    df["url"] = "?metric_id=" + df["metric_id"]
    df["score_pct"] = (df["score"] * 100).round(0)

    display = df[["url", "title", "score_pct"]].copy()

    def _score_styles(_: pd.Series) -> list[str]:
        return [
            f"background-color: {_rag_colour(rag)}; color: {'#ffffff' if rag in ('red', 'green') else '#000000'}; text-align: center"
            for rag in df["rag"]
        ]

    st.dataframe(
        display.style.apply(_score_styles, subset=["score_pct"]),
        column_config={
            "url": st.column_config.LinkColumn("ID", display_text=r"\?metric_id=(.+)"),
            "title": st.column_config.TextColumn("Title"),
            "score_pct": st.column_config.NumberColumn("Score", format="%.0f%%", width="small"),
        },
        hide_index=True,
        width="content",
    )
