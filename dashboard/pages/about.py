from dash import html, dcc, register_page, Input, Output, callback, dash_table
import os
import datetime
register_page(__name__, path_template='/about')

debug = {}
debug["start_time"] = datetime.datetime.now() if not "start+time" in debug else debug["start_time"]
debug["database_engine"] = "Postgres" if os.getenv("POSTGRES_ENDPOINT") else "DuckDB"

try:
    with open('build-date.txt','rt',encoding='utf-8') as q:
        debug["build_date"] = q.read()
except:
    pass

layout = html.Div([
    html.H2("About the Continuous Controls Monitoring Dashboard"),
    html.Div([
        html.P("This dashboard is designed to provide an executive overview of continuous controls monitoring across various business units, teams, and locations."),
        html.P("It allows users to filter data by business unit, team, location, and framework, providing a comprehensive view of compliance and risk management."),
        html.P("The dashboard is built using Dash and Plotly, leveraging a database query cache for efficient data retrieval."),
        html.P("For more information on how to use this dashboard, please refer to the documentation or contact the support team."),
    ], className="about-content"),
    html.H5("Debug info"),
    html.Div([
        dash_table.DataTable(
            data=[{"Variable": k, "Value": v} for k, v in sorted(debug.items())],
            columns=[{"name": "Variable", "id": "Variable"},
                     {"name": "Value", "id": "Value"}],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px'},
            style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
            style_data={'whiteSpace': 'normal', 'height': 'auto'}
        )
    ], className="env-vars-table"),
    html.H5("Contact information"),
    html.Div([
        html.A("mantelgroup.com.au", href="https://mantelgroup.com.au")
    ])      
])
