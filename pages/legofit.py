from dash import html, dcc, dash_table, register_page, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dash_table.Format import Format, Scheme

register_page(__name__, path='/')

# dataset
df = pd.read_csv("pages/lux_sim14000_ResAll_buildingTotal_shuffled.csv")

# ID column
id_column = None
for col in df.columns:
    if col.strip().lower() == "version":
        id_column = col
        break
if id_column is None:
    df.insert(0, "ID", df.index)
    id_column = "ID"

# labels for the parallel coordinates plot
labels = {col: col.replace('_', ' ').title() for col in df.columns}

# last column for the color scale
color_col = df.columns[-1]

# Remove the first column (ID)
dimensions_to_plot = list(df.columns[1:])

fig_parallel = px.parallel_coordinates(
    df,
    dimensions=dimensions_to_plot,
    color=df[color_col],
    labels=labels,
    color_continuous_scale=px.colors.diverging.Tealrose,
)
fig_parallel.update_layout(
    coloraxis_colorbar=dict(title="Qheating"),
    margin=dict(l=35, r=50, t=50, b=60),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font_color="#2C3E50"
)
fig_parallel.update_traces(unselected=dict(line=dict(opacity=0)))

# Scatter plot
scatter_options = {
    "Scatter 1": {"x": "total_idealCooling", "y": "total_idealHeating"},
    "Scatter 2": {"x": "Pareto_TIC (kWh)", "y": "Simulation_TIC (kWh)"},
    "Scatter 3": {"x": "Simulation_TIC (kWh)", "y": "Simulation_TIH (kWh)"},
    "Scatter 4": {"x": "MAPE_cooling", "y": "MAPE_heating"},
}

def create_scatter_figure(option_key):
    option = scatter_options[option_key]
    x_col = option["x"]
    y_col = option["y"]
    df[x_col] = pd.to_numeric(df[x_col], errors='coerce')
    df[y_col] = pd.to_numeric(df[y_col], errors='coerce')
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        hover_data=["ID"]
    )
    fig.update_traces(
        marker=dict(size=8, opacity=0.7),
        selected=dict(marker=dict(color='red', opacity=1, size=10)),
        unselected=dict(marker=dict(opacity=0.3))
    )
    fig.update_layout(
        clickmode='event+select',
        dragmode='select',
        margin=dict(l=30, r=20, t=20, b=60),
        xaxis=dict(showgrid=True, gridcolor="lightgrey", zeroline=True, zerolinecolor="black"),
        yaxis=dict(showgrid=True, gridcolor="lightgrey", zeroline=True, zerolinecolor="black"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#2C3E50",
        uirevision='static'
    )
    return fig

initial_scatter_option = "Scatter 1"
fig_scatter = create_scatter_figure(initial_scatter_option)

# custom styles
CARDHEADER_STYLE = {"backgroundColor": "#2AACFD", "color": "white",
                    "borderRadius": "0px", "borderBottom": "1px solid #2C3E50",
                    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.5)"}
CARD_STYLE = {"borderRadius": "0px", "boxShadow": "0 4px 12px rgba(0, 1, 1, 0.15)",
              "border": "none", "backgroundColor": "#FFFFFF"}
DROPDOWN_STYLE = {"position": "absolute", "top": "480px", "left": "10px",
                  "width": "200px", "zIndex": "2000", "backgroundColor": "rgba(236, 240, 241, 0)",
                  "padding": "2px", "borderRadius": "0px", "border": "1px solid #bdc3c7"}
CHECKBOX_STYLE = {"position": "absolute", "zIndex": "1000", "backgroundColor": "rgba(236, 240, 241, 0)",
                  "padding": "5px", "borderRadius": "5px"}

# simple info icon component
def info_icon(id_str):
    return html.Span("i", id=id_str, style={
        "display": "inline-block",
        "width": "16px",
        "height": "16px",
        "borderRadius": "50%",
        "backgroundColor": "#ccc",
        "color": "white",
        "fontSize": "12px",
        "textAlign": "center",
        "lineHeight": "16px",
        "marginRight": "8px",
        "cursor": "pointer"
    })

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.Div([
                        html.Span("Total Ideal Loads", style={"fontWeight": "bold"}),
                        html.Span("ⓘ", id="tip-total", style={
                            "color": "white", "marginLeft": "10px",
                            "cursor": "pointer",
                            "fontSize": "18px"
                        })
                    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
                    style=CARDHEADER_STYLE
                ),
                dbc.Tooltip("This scatter plot compares total cooling vs. heating demands.",
                            target="tip-total", placement="right-start", style={"zIndex": 3000}),
                dbc.CardBody([
                    dcc.Graph(id="scatter-plot", figure=fig_scatter),
                ])
            ], style=CARD_STYLE),
            width=6
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.Div([
                        html.Span("Parallel Coordinates Plot", style={"fontWeight": "bold"}),
                        html.Span("ⓘ", id="tip-parallel", style={
                            "color": "white", "marginLeft": "10px",
                            "cursor": "pointer",
                            "fontSize": "18px"
                        })
                    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
                    style=CARDHEADER_STYLE
                ),
                dbc.Tooltip("This parallel plot shows multiple simulation dimensions.",
                            target="tip-parallel", placement="left-start", style={"zIndex": 3000}),
                dbc.CardBody([
                    dcc.Graph(id="parallel-plot", figure=fig_parallel)
                ])
            ], style=CARD_STYLE),
            width=6
        )
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.Div([
                        html.Span("Instance Table", style={"fontWeight": "bold"}),
                        html.Span("ⓘ", id="tip-table", style={
                            "color": "white", "marginLeft": "10px",
                            "cursor": "pointer",
                            "fontSize": "18px"
                        })
                    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
                    style=CARDHEADER_STYLE
                ),
                dbc.Tooltip("This table displays simulation data and allows selection.",
                            target="tip-table", placement="right-start", style={"zIndex": 3000}),
                dbc.CardBody([
                    html.Div([
                        dcc.Checklist(
                            id="select-all-checkbox",
                            options=[{"label": "", "value": "select_all"}],
                            value=[],
                            style={**CHECKBOX_STYLE, "top": "1px", "left": "3.20px"}
                        ),
                        dbc.Tooltip("Select All Filtered",
                                    target="select-all-checkbox", placement="top",
                                    style={"zIndex": "3000"}),
                        dcc.Checklist(
                            id="show-selected-checkbox",
                            options=[{"label": "", "value": "show_selected"}],
                            value=[],
                            style={**CHECKBOX_STYLE, "top": "30px", "left": "3.20px"}
                        ),
                        dbc.Tooltip("Show Selected Rows",
                                    target="show-selected-checkbox", placement="top",
                                    style={"zIndex": "3000"}),
                        dash_table.DataTable(
                            id="data-table",
                            columns=[
                                {
                                    "name": col,
                                    "id": col,
                                    "type": "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "text",
                                    "format": Format(precision=3, scheme=Scheme.fixed)
                                        if pd.api.types.is_numeric_dtype(df[col]) else None
                                }
                                for col in df.columns if col != id_column
                            ],
                            data=df.to_dict("records"),
                            row_selectable="multi",
                            filter_action="native",
                            sort_action="native",
                            page_size=10,
                            style_table={'minWidth': '100%'},
                            style_data_conditional=[],
                        )
                    ], style={"position": "relative", "overflow": "auto",
                              "height": "420px", "border": "1px solid #bdc3c7",
                              "borderRadius": "0px"})
                ])
            ], style=CARD_STYLE),
            width=6
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.Div([
                        html.Span("3D Model", style={"fontWeight": "bold"}),
                        html.Span("ⓘ", id="tip-model", style={
                            "color": "white", "marginLeft": "10px",
                            "cursor": "pointer",
                            "fontSize": "18px"
                        })
                    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
                    style=CARDHEADER_STYLE
                ),
                dbc.Tooltip("This embedded view displays the 3D design model.",
                            target="tip-model", placement="left-start", style={"zIndex": 3000}),
                dbc.CardBody([
                    html.Iframe(src="https://omurbugra.github.io/Graph3dv2",
                                style={"width": "100%", "height": "414px", "border": "none", "borderRadius": "0px"})
                ])
            ], style=CARD_STYLE),
            width=6
        )
    ])
], fluid=True, style={"backgroundColor": "#FFFFFF", "padding": "20px"})

