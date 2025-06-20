import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

NAVBAR_STYLE = {
    "backgroundColor": "#2AACFD",
    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.8)",
    "borderRadius": "0px",
    "padding": "15px 10px"
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

header = html.Header(
    html.Div(
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "flex-end",
            "padding": "8px 25px",
            "height": "100%"  # içerik dikey hizalansın
        },
        children=[
            html.H1([
                "⚡ Energy+ Parametric Dashboard",
                html.Span(
                    "  by Ömür Buğra Gündüz",
                    style={
                        "fontSize": "0.66rem",       # yaklaşık 1/3
                        "color": "#FFFFFF",
                        "marginLeft": "8px",
                        "verticalAlign": "baseline"
                    }
                )
            ],
            style={
                "fontSize": "2rem",
                "fontWeight": "bold",
                "color": "white",
                "margin": 0
            }),
        ]
    ),
    style={
        "background": "#2AACFD",
        "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.4)",
        "position": "fixed",
        "top": "0",
        "width": "100vw",
        "left": 0,
        "zIndex": "1000",
        "height": "55px"
    }
)


# Grouped tabs container
tabs_container = html.Div(
    dbc.Nav(
        [
            dbc.NavLink("All solutions", href="/", active="exact", className="grouped-nav-link"),
            dbc.NavLink("Optimized", href="/legofit2", active="exact", className="grouped-nav-link"),
        ],
        pills=True,
        className="tabs-group"  # container for grouped links
    ),
    style={"overflowX": "auto", "whiteSpace": "nowrap", "marginTop": "10px", "padding": "0 20px"}
)

combined_header = html.Div(
    [header, tabs_container],
    style={"marginTop": "80px"}  # accounts for fixed header height
)

app.layout = dbc.Container([
    combined_header,
    # Provide the current URL so callbacks can detect the page.
    dcc.Location(id="url", refresh=False),
    dash.page_container,
], fluid=True)

# Import callback files .
import callbacks
import callbacks_legofit2

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
