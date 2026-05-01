from dash import html, dcc, register_page, Input, Output, callback
import plotly.express as px
from dash import dash_table,html
import plotly.graph_objects as go
from database import DatabaseQueryCache
import pandas as pd
from dash.dash_table.Format import Format, Scheme
from colour_config import COLOURS

register_page(__name__, path="/metrics")

db_cache = DatabaseQueryCache(max_cache_age_minutes=15)

layout = html.Div([
    html.H2("Metrics"),

    html.Div([
        html.Div([
            html.H5("Business Unit"),
            dcc.Dropdown(
                id="business-unit-filter2",
                options=[],
                multi=False,
                placeholder="Select business unit",
                clearable=True,
            ),
            html.H5("Team"),
            dcc.Dropdown(
                id="team-filter2",
                options=[],
                multi=False,
                placeholder="Select team",
                clearable=True,
            ),
            html.H5("Location"),
            dcc.Dropdown(
                id="location-filter2",
                options=[],
                multi=False,
                placeholder="Select location",
                clearable=True,
            ),
            html.H5("Framework"),
            dcc.Dropdown(
                id="framework-filter2",
                options=[
                    {"label": "CIS 8.1", "value": "CIS 8.1"}
                ],
                multi=False,
                placeholder="Select Framework",
                clearable=False,
                value='CIS 8.1'
            ),
        ], className="col-3 filter-sidebar border"),
        

        # Graph on right (9 columns wide)
        html.Div([
            html.Div(id="graph-executive-overview2")
        ], className="col-9 border p-3")
    ], className="row")
])

# == filter callbacks
@callback(
    Output("business-unit-filter2", "options"),
    Input("business-unit-filter2", "id")
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
    Output("team-filter2", "options"),
    Input("team-filter2", "id")
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
    Output("location-filter2", "options"),
    Input("location-filter2", "id")
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
    Output("framework-filter2", "options"),
    Input("framework-filter2", "id")
)
def populate_framework_options(_):
    query = "SELECT DISTINCT framework FROM mrt_v2_framework ORDER BY framework"
    try:
        df = db_cache.query(query)
        return [{"label": s, "value": s} for s in df["framework"]]
    except Exception as e:
        print(f"[ERROR] Failed to load location options: {e}")
        return [{"label": "Error loading options", "value": ""}]

# == graph callbacks
@callback(
    Output("graph-executive-overview2", "children"),
    Input("business-unit-filter2", "value"),
    Input("team-filter2", "value"),
    Input("location-filter2", "value"),
    Input("framework-filter2", "value"),
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

    base_sql = metrics_query(params)

    try:
        df = db_cache.query(base_sql, params)
    except Exception as e:
        print(f"Something went wrong with the SQL query - {e}")

    # Metrics
    df['title'] = df.apply(
        lambda row: row['title'] if row['title'].startswith('[') and '](/metric/' in row['title']
        else f"[{row['title']}](/metric/{row['metric_id']})",
        axis=1
    )

    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    df = df.sort_values(by='score', ascending=True)

    fig = dash_table.DataTable(
        id='table',
        columns=[
            {"name": "Id" , "id" : "metric_id"},
            {"name": "Title", "id": "title", "presentation": "markdown"},
            {
                "name": "Score",
                "id": "score",
                "type": "numeric",
                "format": Format(precision=0, scheme=Scheme.percentage)
            },
        ],
        data=df.to_dict('records'),
        page_size=20,
        style_table={
            'height': '700px', 
            'overflowY': 'auto',
            'backgroundColor': COLOURS['filler'],
            'border': '1px solid ' + COLOURS['border'],
            'borderRadius': '5px',
            'padding': '5px',
            'width': '100%'
        },
        style_cell={
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
            'fontSize': '14px',
            'textAlign': 'left',
            'verticalAlign': 'middle',
            'padding': '5px',
            'maxWidth': '300px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'whiteSpace': 'normal',
            'lineHeight': '1.2'
        },
        style_data={
            'backgroundColor': 'transparent',
            'height': '30px'
        },
        style_header={
            'textAlign': 'left',
            'fontWeight': 'bold',
            'backgroundColor': COLOURS['filler2'],
            'borderBottom': '1px solid ' + COLOURS['border'],
            'color': COLOURS['navbar'],
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
            'fontSize': '14px',
            'verticalAlign': 'middle',
            'padding': '5px'
        },
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'metric_id'
                },
                'width': '5%',
                'textAlign': 'left'
            },
            {
                'if': {
                    'column_id': 'title'
                },
                'width': '85%',
                'textAlign': 'left',
            },
            {
                'if': {
                    'column_id': 'score'
                },
                'width': '10%',
                'textAlign': 'center'
            },
            {
                'if': {
                    'column_id': 'score',
                    'filter_query': '{rag} = "amber"',
                },
                'backgroundColor': COLOURS['categories']['amber'],
                'color': "#000000"
            },
            {
                'if': {
                    'column_id': 'score',
                    'filter_query': '{rag} = "red"',
                },
                'backgroundColor': COLOURS['categories']['red'],
                'color': "#FFFFFF"
            },
            {
                'if': {
                    'column_id': 'score',
                    'filter_query': '{rag} = "green"',
                },
                'backgroundColor': COLOURS['categories']['green'],
                'color': "#FFFFFF"
            }
        ]
    )
    return fig

def metrics_query(filters):
    placeholders = ''
    if filters and len(filters) > 0:
        conditions = []
        for i, (field, value) in enumerate(filters.items()):
            conditions.append(f"{field} = :{field}")
        placeholders = " AND " + " AND ".join(conditions)

    return f'''
select
	S.upload_date,
  S.metric_id,
  L.title,
  SUM(S.metric_numerator) / SUM(S.metric_denominator) as score,
  L.slo_limit,
  L.slo_target,
  L.weight,
  CASE
  	WHEN SUM(S.metric_numerator) / SUM(S.metric_denominator) < L.slo_limit then 'red'
	WHEN SUM(S.metric_numerator) / SUM(S.metric_denominator) >= L.slo_target then 'green'
	else 'amber'
    END as rag
from mrt_v2_summary S
INNER JOIN mrt_v2_metric_library L on L.unique_sk_metric_id_upload_date = S.unique_sk_metric_id_upload_date
INNER JOIN mrt_v2_framework F on F.metric_id = S.metric_id
WHERE
    L.in_production is true and L.in_management is true and S.is_latest = true
{placeholders}
GROUP BY
	S.upload_date,
	S.metric_id,
	L.slo_limit,
    L.title,
	L.slo_target,
	L.weight

  '''
