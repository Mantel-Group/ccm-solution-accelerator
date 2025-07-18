from dash import html, dcc, register_page, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseQueryCache
from colour_config import COLOURS

register_page(__name__, path="/")

db_cache = DatabaseQueryCache(max_cache_age_minutes=15)

layout = html.Div([
    html.H2("Executive Overview", className="mb-4"),
    html.Div([
        html.Div([
            html.Div([
                html.H5("Business Unit"),
                dcc.Dropdown(
                    id="business-unit-filter",
                    options=[],
                    multi=False,
                    placeholder="Select business unit",
                    clearable=True,
                    className="mb-3"
                ),
                html.H5("Team"),
                dcc.Dropdown(
                    id="team-filter",
                    options=[],
                    multi=False,
                    placeholder="Select team",
                    clearable=True,
                    className="mb-3"
                ),
                html.H5("Location"),
                dcc.Dropdown(
                    id="location-filter",
                    options=[],
                    multi=False,
                    placeholder="Select location",
                    clearable=True,
                    className="mb-3"
                ),
                html.H5("Framework"),
                dcc.Dropdown(
                    id="framework-filter",
                    options=[
                        {"label": "CIS 8.1", "value": "CIS 8.1"}
                    ],
                    multi=False,
                    placeholder="Select Framework",
                    clearable=False,
                    value='CIS 8.1',
                    className="mb-3"
                ),
            ], className="filter-sidebar")
        ], className="col-3 sidebar-container"),
        
        html.Div([
            html.Div([
                dcc.Graph(
                    id="graph-executive-overview", 
                    style={'width': '100%', 'height': '450px'}
                )
            ], className="executive-overview-container"),
            
            html.Div([
                html.Div([
                    dcc.Graph(
                        id="dimension-graph", 
                        className="graph",
                        style={'height': '400px', 'width': '100%'}
                    )
                ], className="col-6 sub-graph"),
                html.Div([
                    dcc.Graph(
                        id="category-graph", 
                        className="graph",
                        style={'height': '400px', 'width': '100%'}
                    )
                ], className="col-6 sub-graph")
            ], className="row")
        ], className="col-9 main-content")
    ], className="row")
])

# == filter callbacks
@callback(
    Output("business-unit-filter", "options"),
    Input("business-unit-filter", "id")
)
def populate_business_unit_options(_):
    query = "SELECT DISTINCT business_unit FROM mrt_v2_summary where is_latest is true ORDER BY business_unit"
    try:
        df = db_cache.query(query)
        return [{"label": s, "value": s} for s in df["business_unit"]]
    except Exception as e:
        print(f"[ERROR] Failed to load location options: {e}")
        return [{"label": "Error loading options", "value": ""}]

@callback(
    Output("team-filter", "options"),
    Input("team-filter", "id")
)
def populate_team_options(_):
    query = "SELECT DISTINCT team FROM mrt_v2_summary where is_latest is true ORDER BY team"
    try:
        df = db_cache.query(query)
        return [{"label": s, "value": s} for s in df["team"]]
    except Exception as e:
        print(f"[ERROR] Failed to load location options: {e}")
        return [{"label": "Error loading options", "value": ""}]

@callback(
    Output("location-filter", "options"),
    Input("location-filter", "id")
)
def populate_location_options(_):
    query = "SELECT DISTINCT location FROM mrt_v2_summary where is_latest is true ORDER BY location"
    try:
        df = db_cache.query(query)
        return [{"label": s, "value": s} for s in df["location"]]
    except Exception as e:
        print(f"[ERROR] Failed to load location options: {e}")
        return [{"label": "Error loading options", "value": ""}]

@callback(
    Output("framework-filter", "options"),
    Input("framework-filter", "id")
)
def populate_framework_options(_):
    query = "SELECT DISTINCT framework FROM mrt_v2_framework ORDER BY framework"
    try:
        df = db_cache.query(query)
        return [{"label": s, "value": s} for s in df["framework"]]
    except Exception as e:
        print(f"[ERROR] Failed to load framework options: {e}")
        return [{"label": "Error loading options", "value": None}]

# == graph callbacks
@callback(
    Output("graph-executive-overview", "figure"),
    Output("dimension-graph"         , "figure"),
    Output("category-graph"          , "figure"),
    Output("alert-message"           , "children"),
    Output("alert-message"           , "className"),
    Input("business-unit-filter"     , "value"),
    Input("team-filter"              , "value"),
    Input("location-filter"          , "value"),
    Input("framework-filter"         , "value"),
)
def update_graph(selected_business_unit, selected_team, selected_location, selected_framework):
    params = {}
    if selected_business_unit:
        params['business_unit'] = selected_business_unit
    if selected_team:
        params['team'] = selected_team
    if selected_location:
        params['location'] = selected_location
    if selected_framework:
        params['framework'] = selected_framework

    base_sql = overview_query(params)

    try:
        df_overview = db_cache.query(base_sql, params)
    except Exception as e:
        print(f"Something went wrong with the SQL query - {e}")
        return go.Figure(), "Database error: unable to run query.", "alert alert-danger"

    if df_overview.empty:
        return go.Figure(), "No data available for the selected filters.", "alert alert-danger"

    # == Overview graph
    fig_overview = px.bar(
        df_overview, x="upload_date", y="score",
        color="rag",
        color_discrete_map=COLOURS['categories'],
        title="Aggregated Score Over Time",
        text_auto=True
    )
    fig_overview.update_layout(
        paper_bgcolor=COLOURS['chart_bg'],
        plot_bgcolor=COLOURS['chart_bg'],
        margin=dict(l=50, r=50, t=80, b=50),
        height=450,
        autosize=True,
        title={
            'text': "Aggregated Score Over Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': COLOURS['text_primary'], 'family': 'Inter'}
        },
        font={'family': 'Inter', 'color': COLOURS['text_primary']},
        xaxis={'gridcolor': '#f0f0f0', 'gridwidth': 1},
        yaxis={'gridcolor': '#f0f0f0', 'gridwidth': 1}
    )
    fig_overview.update_yaxes(range=[0, 1], tickformat=".0%", title=None)
    fig_overview.update_xaxes(title=None)
    fig_overview.update_layout(showlegend=False, xaxis_type="category")
    fig_overview.update_traces(textposition='outside', textfont_size=12)
    fig_overview.add_trace(go.Scatter(
        x=df_overview["upload_date"], 
        y=df_overview["slo_target"], 
        mode="lines", 
        name="Target", 
        line=dict(color=COLOURS['categories']['green'], width=3, dash='dash')
    ))
    fig_overview.add_trace(go.Scatter(
        x=df_overview["upload_date"], 
        y=df_overview["slo_limit"], 
        mode="lines", 
        name="Limit", 
        line=dict(color=COLOURS['categories']['amber'], width=3, dash='dot')
    ))

    # Dimension graph
    base_sql = dimension_query('business_unit',params)
    df_business_unit= db_cache.query(base_sql, params)

    fig_business_unit = px.bar(
        df_business_unit,
        y="business_unit",
        x="score",
        orientation="h",
        color="rag",
        color_discrete_map=COLOURS['categories'],
        title="Latest Score by Business Unit",
        text_auto=True
    )
    
    fig_business_unit.update_layout(
        paper_bgcolor=COLOURS['chart_bg'],
        plot_bgcolor=COLOURS['chart_bg'],
        margin=dict(l=50, r=50, t=60, b=40),
        height=400,
        title={
            'text': "Latest Score by Business Unit",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': COLOURS['text_primary'], 'family': 'Inter'}
        },
        font={'family': 'Inter', 'color': COLOURS['text_primary']},
        xaxis={'gridcolor': '#f0f0f0', 'gridwidth': 1},
        yaxis={'gridcolor': '#f0f0f0', 'gridwidth': 1}
    )
    fig_business_unit.update_xaxes(range=[0, 1], tickformat=".0%", title=None)
    fig_business_unit.update_yaxes(title=None)
    fig_business_unit.update_layout(showlegend=False, yaxis_type="category")
    fig_business_unit.update_traces(textposition='outside', textfont_size=11)
    fig_business_unit.add_trace(go.Scatter(
        x=df_business_unit["slo_target"],
        y=df_business_unit["business_unit"],
        mode="lines",
        name="Target",
        line=dict(color=COLOURS['categories']['green'], width=2, dash='dash')
    ))
    fig_business_unit.add_trace(go.Scatter(
        x=df_business_unit["slo_limit"],
        y=df_business_unit["business_unit"],
        mode="lines",
        name="Limit",
        line=dict(color=COLOURS['categories']['amber'], width=2, dash='dot')
    ))

    # category graph
    base_sql = dimension_query('domain',params)
    df_domains = db_cache.query(base_sql, params)
    
    fig_domain = px.bar(
        df_domains,
        y="domain",
        x="score",
        orientation="h",
        color="rag",
        color_discrete_map=COLOURS['categories'],
        title="Latest Score by Cyber Domain",
        text_auto=True
    )
    
    fig_domain.update_layout(
        paper_bgcolor=COLOURS['chart_bg'],
        plot_bgcolor=COLOURS['chart_bg'],
        margin=dict(l=50, r=50, t=60, b=40),
        height=400,
        title={
            'text': "Latest Score by Cyber Domain",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': COLOURS['text_primary'], 'family': 'Inter'}
        },
        font={'family': 'Inter', 'color': COLOURS['text_primary']},
        xaxis={'gridcolor': '#f0f0f0', 'gridwidth': 1},
        yaxis={'gridcolor': '#f0f0f0', 'gridwidth': 1}
    )
    fig_domain.update_xaxes(range=[0, 1], tickformat=".0%", title=None)
    fig_domain.update_yaxes(title=None)
    fig_domain.update_layout(showlegend=False, yaxis_type="category")
    fig_domain.update_traces(textposition='outside', textfont_size=11)
    fig_domain.add_trace(go.Scatter(
        x=df_domains["slo_target"],
        y=df_domains["domain"],
        mode="lines",
        name="Target",
        line=dict(color=COLOURS['categories']['green'], width=2, dash='dash')
    ))
    fig_domain.add_trace(go.Scatter(
        x=df_domains["slo_limit"],
        y=df_domains["domain"],
        mode="lines",
        name="Limit",
        line=dict(color=COLOURS['categories']['amber'], width=2, dash='dot')
    ))

    return fig_overview, fig_business_unit, fig_domain, "", "alert alert-danger d-none"

def overview_query(filters):
    placeholders = ''
    if filters and len(filters) > 0:
        conditions = []
        for i, (field, value) in enumerate(filters.items()):
            conditions.append(f"{field} = :{field}")
        placeholders = "AND " + " AND ".join(conditions)

    return f'''SELECT
  Q1.upload_date,
  SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) as score,
  SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) as slo_limit,
  SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) as slo_target,
  CASE
  	WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) < SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) then 'red'
	WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) >= SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) then 'green'
	else 'amber'
	END as rag
FROM
(
select
	S.upload_date,
  S.metric_id,
  SUM(S.metric_numerator) / SUM(S.metric_denominator) * AVG(L.weight) as weighted_score,
  L.slo_limit * AVG(L.weight) as weighted_slo_limit,
  L.slo_target * AVG(L.weight) as weighted_slo_target,
  L.weight
from mrt_v2_summary S
INNER JOIN mrt_v2_metric_library L on L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
INNER JOIN mrt_v2_framework F on F.metric_id = S.metric_id
WHERE
    L.in_production is true and L.in_executive is true
{placeholders}
GROUP BY
	S.upload_date,
	S.metric_id,
	L.slo_limit,
	L.slo_target,
	L.weight
) Q1
GROUP BY
  Q1.upload_date
ORDER BY
  Q1.upload_date asc
  '''

def dimension_query(dimension,filters):
    placeholders = ''
    if filters and len(filters) > 0:
        conditions = []
        for i, (field, value) in enumerate(filters.items()):
            conditions.append(f"{field} = :{field}")
        placeholders = "AND " + " AND ".join(conditions)

    return f'''SELECT
  Q1.{dimension},
  SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) as score,
  SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) as slo_limit,
  SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) as slo_target,
  CASE
  	WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) < SUM(Q1.weighted_slo_limit) / NULLIF(SUM(Q1.weight), 0) then 'red'
	WHEN SUM(Q1.weighted_score) / NULLIF(SUM(Q1.weight), 0) >= SUM(Q1.weighted_slo_target) / NULLIF(SUM(Q1.weight), 0) then 'green'
	else 'amber'
	END as rag
FROM
(
select
  {dimension},
  S.metric_id,
  SUM(S.metric_numerator) / SUM(S.metric_denominator) * AVG(L.weight) as weighted_score,
  L.slo_limit * AVG(L.weight) as weighted_slo_limit,
  L.slo_target * AVG(L.weight) as weighted_slo_target,
  L.weight
from mrt_v2_summary S
INNER JOIN mrt_v2_metric_library L on L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
INNER JOIN mrt_v2_framework F on F.metric_id = S.metric_id
WHERE
    L.in_production is true and L.in_executive is true and S.is_latest is true
{placeholders}
GROUP BY
	{dimension},
	S.metric_id,
	L.slo_limit,
	L.slo_target,
	L.weight
) Q1
GROUP BY
  Q1.{dimension}

  '''
