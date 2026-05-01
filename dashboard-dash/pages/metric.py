from dash import html, dcc, register_page, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseQueryCache
from colour_config import COLOURS

register_page(__name__, path_template='/metric/<metric>')

db_cache = DatabaseQueryCache(max_cache_age_minutes=15)

layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.H2(id="metric-title"),
    html.P(id="metric-description"),

    html.Div([
        html.Div([
            html.H5("Business Unit"),
            dcc.Dropdown(
                id="business-unit-filter3",
                options=[],
                multi=False,
                placeholder="Select business unit",
                clearable=True,
            ),
            html.H5("Team"),
            dcc.Dropdown(
                id="team-filter3",
                options=[],
                multi=False,
                placeholder="Select team",
                clearable=True,
            ),
            html.H5("Location"),
            dcc.Dropdown(
                id="location-filter3",
                options=[],
                multi=False,
                placeholder="Select location",
                clearable=True,
            ),
        ], className="col-3 filter-sidebar border"),
        
        # Graph on right (9 columns wide)
        html.Div([
            html.Div([
                dcc.Graph(id="graph-executive-overview3")
            ], className="p-3 border"),

            html.Div(className="table-container", children=[
                html.Div(className="metrics-header-container", children=[
                    html.H2("Detail", className="metrics-header")
                ]),
                html.Div(id="detail-table", className="metrics-table")
            ])
        ], className="col-9")
    ], className="row g-3")
])

@callback(
    Output("metric-title", "children"),
    Output("metric-description", "children"),
    Input("url", "pathname")
)
def update_metric_title(pathname):
    try:
        # Extract metric from URL like /metric/some_metric
        metric = pathname.split("/metric/")[1]
    except IndexError:
        return "Metric not found"
    
    query = f"SELECT title,description FROM mrt_v2_metric_library WHERE is_latest is true and metric_id = :metric_id"
    df = db_cache.query(query, params={ 'metric_id' : metric })
    if not df.empty:
        return f"{metric} - {df.iloc[0]['title']}",df.iloc[0]['description']
    else:
        return f"{metric} - No description found","None found"

# == filter callbacks
@callback(
    Output("business-unit-filter3", "options"),
    Input("business-unit-filter3", "id")
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
    Output("team-filter3", "options"),
    Input("team-filter3", "id")
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
    Output("location-filter3", "options"),
    Input("location-filter3", "id")
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
    Output("graph-executive-overview3", "figure"),
    Output("detail-table", "children"),
    Input("url", "pathname"),
    Input("business-unit-filter3", "value"),
    Input("team-filter3", "value"),
    Input("location-filter3", "value"),
)
def update_graph(pathname, selected_business_unit, selected_team, selected_location):
    params = {}
    try:
        # Extract metric from URL like /metric/some_metric
        params['metric_id'] = pathname.split("/metric/")[1]
    except IndexError:
        return "Metric not found"
    
    if selected_business_unit:
        params['business_unit'] = selected_business_unit
    if selected_team:
        params['team'] = selected_team
    if selected_location:
        params['location'] = selected_location

    base_sql = metric_query(params)

    try:
        df = db_cache.query(base_sql, params)
    except Exception as e:
        print(f"Something went wrong with the SQL query - {e}")

    # Metric Overview
    fig1 = px.bar(
        df, x="upload_date", y="score",
        color="rag",
        color_discrete_map=COLOURS['categories'],
        title="Individual metric score over time",
        text_auto=True
    )
    fig1.update_layout(
        paper_bgcolor=COLOURS['filler'],
        plot_bgcolor=COLOURS['filler2'],
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig1.update_yaxes(range=[0, 1], tickformat=".0%")
    fig1.update_xaxes(title=None)
    fig1.update_yaxes(title=None)
    fig1.update_layout(showlegend=False)
    fig1.update_layout(xaxis_type="category")
    fig1.add_trace(
        go.Scatter(
            x=df["upload_date"],
            y=df["slo_target"],
            mode="lines",
            name="slo_target",
            line=dict(color=COLOURS['categories']['green'])
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=df["upload_date"],
            y=df["slo_limit"],
            mode="lines",
            name="slo_limit",
            line=dict(color=COLOURS['categories']['amber'])
        )
    )

    # Table
    try:
        df = db_cache.query(detail_query(params), params)
    except Exception as e:
        print(f"Something went wrong with the SQL query - {e}")

    df['rag'] = df.apply(lambda row: "red" if row['compliance'] == 0 else "green" if row['compliance'] == 1 else "amber", axis = 1)

    # Format compliance: show integers as-is, decimals with one decimal place
    df['compliance'] = df['compliance'].apply(lambda x: str(int(x)) if x in [0, 1] else f"{x:.1f}")

    table = dash_table.DataTable(
        data=df.to_dict(orient="records"),
        columns=[
            {"name": "Date"       , "id" : "upload_date"},
            {"name": "Resource"   , "id" : "resource"},
            {"name": "Owner"      , "id" : "owner"},
            {"name": "Detail"     , "id" : "detail"},
            {"name": "Compliance" , "id" : "compliance"},
        ],
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
                    'column_id': 'upload_date'
                },
                'width': '15%',
                'textAlign': 'left'
            },
            {
                'if': {
                    'column_id': 'resource'
                },
                'width': '25%',
                'textAlign': 'left'
            },
            {
                'if': {
                    'column_id': 'owner'
                },
                'width': '20%',
                'textAlign': 'left'
            },
            {
                'if': {
                    'column_id': 'detail'
                },
                'width': '30%',
                'textAlign': 'left'
            },
            {
                'if': {
                    'column_id': 'compliance'
                },
                'width': '10%',
                'textAlign': 'center'
            },
            {
                'if': {
                    'column_id': 'compliance',
                    'filter_query': '{rag} = "amber"',
                },
                'backgroundColor': COLOURS['categories']['amber'],
                'color': "#000000"
            },
            {
                'if': {
                    'column_id': 'compliance',
                    'filter_query': '{rag} = "red"',
                },
                'backgroundColor': COLOURS['categories']['red'],
                'color': "#FFFFFF"
            },
            {
                'if': {
                    'column_id': 'compliance',
                    'filter_query': '{rag} = "green"',
                },
                'backgroundColor': COLOURS['categories']['green'],
                'color': "#FFFFFF"
            }
        ]
    )
    return fig1,table

def metric_query(filters):
    placeholders = ''
    if filters and len(filters) > 0:
        conditions = []
        for i, (field, value) in enumerate(filters.items()):
            if field == 'metric_id':
                conditions.append(f"L.{field} = :{field}")
            else:
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

def detail_query(filters):
    placeholders = ''
    if filters and len(filters) > 0:
        conditions = []
        for i, (field, value) in enumerate(filters.items()):
            conditions.append(f"{field} = :{field}")
        placeholders = "AND " + " AND ".join(conditions)

    return f'''SELECT
        upload_date,
        resource,
        owner,
        compliance,
        detail
    from
        mrt_v2_detail
    where compliance < 10
    {placeholders}
    order by compliance
  '''
