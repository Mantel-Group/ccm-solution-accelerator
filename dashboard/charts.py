import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from colours import get_rag_colours


def _base_layout(fig: go.Figure, title: str, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        autosize=True,
        title={"text": title, "x": 0.5, "xanchor": "center"},
        showlegend=False,
        margin=dict(l=50, r=50, t=60, b=40),
    )
    return fig


def score_over_time(df: pd.DataFrame, title: str = "Aggregated Score Over Time") -> go.Figure:
    rag = get_rag_colours()
    fig = px.bar(
        df,
        x="upload_date",
        y="score",
        color="rag",
        color_discrete_map=rag,
        text_auto=True,
    )
    fig = _base_layout(fig, title, height=450)
    fig.update_yaxes(range=[0, 1], tickformat=".0%", title=None)
    fig.update_xaxes(title=None, type="category")
    fig.update_traces(textposition="outside", textfont_size=12)
    fig.add_trace(go.Scatter(
        x=df["upload_date"], y=df["slo_target"],
        mode="lines", name="Target",
        line=dict(color=rag["green"], width=3, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=df["upload_date"], y=df["slo_limit"],
        mode="lines", name="Limit",
        line=dict(color=rag["amber"], width=3, dash="dot"),
    ))
    return fig


def horizontal_bar(df: pd.DataFrame, y_col: str, title: str) -> go.Figure:
    rag = get_rag_colours()
    fig = px.bar(
        df,
        y=y_col,
        x="score",
        orientation="h",
        color="rag",
        color_discrete_map=rag,
        text_auto=True,
    )
    fig = _base_layout(fig, title, height=400)
    fig.update_xaxes(range=[0, 1], tickformat=".0%", title=None)
    fig.update_yaxes(title=None, type="category")
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.add_trace(go.Scatter(
        x=df["slo_target"], y=df[y_col],
        mode="lines", name="Target",
        line=dict(color=rag["green"], width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=df["slo_limit"], y=df[y_col],
        mode="lines", name="Limit",
        line=dict(color=rag["amber"], width=2, dash="dot"),
    ))
    return fig
