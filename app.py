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

header = dbc.Navbar(
    dbc.Container(
        dbc.Row([
            dbc.Col(
                html.Img(
                    src="https://www.legofit.eu/wp-content/uploads/2023/09/white.svg",
                    height="60px"
                ),
                width="auto"
            ),
            dbc.Col(
                html.Div([
                    html.Div(
                        "Adaptable technological solutions based on early design actions for",
                        style={"fontSize": "1em", "fontWeight": "500", "color": "white"}
                    ),
                    html.Div(
                        "the construction and renovation of Energy Positive Homes",
                        style={"fontSize": "1em", "fontWeight": "500", "color": "white"}
                    )
                ]),
                width="auto", style={"marginLeft": "10px"}
            )
        ], align="center", className="w-100 flex-nowrap"),
        fluid=True
    ),
    style=NAVBAR_STYLE,
    color="#2C3E50",
    className="mb-2"
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
    style={"marginTop": "10px"}
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

if __name__ == "__main__":
    app.run_server(debug=True)
