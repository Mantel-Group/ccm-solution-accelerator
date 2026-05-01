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
    html.H4("Support Information"),
    html.Div([
        html.P("For support and information:"),
        html.Ul([
            html.Li([
                "View source code and documentation: ",
                html.A("GitHub Repository", href="https://github.com/mantel-group/ccm-solution-accelerator/", target="_blank")
            ]),
            html.Li([
                "To report issues or request features: ",
                html.A("Create a GitHub Issue", href="https://github.com/mantel-group/ccm-solution-accelerator/issues/new", target="_blank"),
            ])
        ])
    ]),
    
    html.H4("License"),
    html.Div([
        html.P("This software has been provided by Mantel Group to your organisation under the following terms:"),
        html.Ul([
            html.Li("✅ You are free to run this software in any way that suits your organisation's needs"),
            html.Li("✅ You may modify and extend the software to meet your specific requirements"),
            html.Li("✅ You may customize configurations, add new features, or integrate with your existing systems"),
            html.Li("❌ You are not permitted to share this code outside of your organisation"),
            html.Li("❌ Distribution, resale, or sharing with external parties is prohibited"),
            html.Li([
                "🤝 We encourage you to contribute back to the project by submitting ",
                html.A("pull requests", href="https://github.com/mantel-group/ccm-solution-accelerator/pulls", target="_blank"),
                " for new features, collectors, or metrics that could benefit the broader community"
            ])
        ]),
    ]),
    html.H4("Contact us"),
    html.Div([
        html.Li([
            "Want to extend this accelerator to suite your environment? ",
            html.A("Contact us", href="https://mantelgroup.com.au/contact", target="_blank"),
            
        ]),
        html.Li([
                "Visit our website: ",
                html.A("mantelgroup.com.au", href="https://mantelgroup.com.au", target="_blank")
            ]),
    ])
])
