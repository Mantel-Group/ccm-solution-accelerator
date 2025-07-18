from dash import html, page_container

def get_layout():
    return html.Div([
        html.Nav([
            html.Div([
                html.A([
    html.Img(
        src="/assets/mantel.png", 
        alt="Mantel Group Logo", 
        height="30",
        className="d-inline-block align-text-top me-2"
    ),
    "Mantel Group - Continuous Controls Monitoring"
], className="navbar-brand", href="/"),
                html.Button(
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    **{
                        "data-bs-toggle": "collapse",
                        "data-bs-target": "#navbarNav",
                        "aria-controls": "navbarNav",
                        "aria-expanded": "false",
                        "aria-label": "Toggle navigation"
                    }
                ),
                html.Div([
                    html.Ul([
                        html.Li(html.A("Overview", className="nav-link", href="/"), className="nav-item"),
                        html.Li(html.A("Metrics", className="nav-link", href="/metrics"), className="nav-item"),
                        html.Li(html.A("About", className="nav-link", href="/about"), className="nav-item"),
                    ], className="navbar-nav me-auto mb-2 mb-lg-0")
                ], className="collapse navbar-collapse", id="navbarNav")
            ], className="container-fluid")
        ], className="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"),

        html.Div(id="alert-message", className="alert alert-danger d-none mt-5 pt-4", role="alert"),
        html.Div(id="success-message", className="alert alert-success d-none mt-5 pt-4", role="alert"),

        html.Div(page_container, className="container mt-5 pt-4")
    ])
