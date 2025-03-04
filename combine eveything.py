from dash import Dash, html, dcc, dash_table, callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

# Load your dataset. Update the path as needed.
df = pd.read_csv(r"C:\Users\Synho\Desktop\everything\Görselleştirme\revise\parallel - combine.csv")

# Check for an ID column in a case-insensitive manner.
id_column = None
for col in df.columns:
    if col.strip().lower() == "id":
        id_column = col
        break
if id_column is None:
    df.insert(0, "ID", df.index)
    id_column = "ID"

# Create pretty labels for the parallel coordinates plot.
labels = {col: col.replace('_', ' ').title() for col in df.columns}

# Use the last column for the color scale.
color_col = df.columns[-1]

# Remove the first column (ID) and the color column from the displayed dimensions.
dimensions_to_plot = list(df.columns[1:])  # remove first column
if color_col in dimensions_to_plot:
    dimensions_to_plot.remove(color_col)

# Build the parallel coordinates plot using the specified dimensions.
fig_parallel = px.parallel_coordinates(
    df,
    dimensions=dimensions_to_plot,
    color=df[color_col],
    labels=labels,
    color_continuous_scale=px.colors.diverging.Tealrose,
)
fig_parallel.update_layout(coloraxis_colorbar=dict(title="Qheating"))
fig_parallel.update_traces(unselected=dict(line=dict(opacity=0)))

# -------------------------------
# SCATTER PLOT SETUP
# -------------------------------
# Choose two columns for the scatter plot.
scatter_x = "U_ground"
scatter_y = "U_wall"

# Convert to numeric if not already.
df[scatter_x] = pd.to_numeric(df[scatter_x], errors='coerce')
df[scatter_y] = pd.to_numeric(df[scatter_y], errors='coerce')

# Create the scatter plot. Note the hover_data includes the ID.
fig_scatter = px.scatter(
    df,
    x=scatter_x,
    y=scatter_y,
    hover_data=[id_column],
    title="Interactive Scatter Plot"
)
# Set marker styles for selected and unselected points.
fig_scatter.update_traces(
    marker=dict(size=8, opacity=0.7),
    selected=dict(marker=dict(color='red', opacity=1, size=10)),
    unselected=dict(marker=dict(opacity=0.3))
)

# Initialize the Dash app with Bootstrap styling.
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# App layout: scatter plot and parallel plot side-by-side on top; data table at the bottom.
app.layout = html.Div([
    dbc.Row([
        dbc.Col(dcc.Graph(id="scatter-plot", figure=fig_scatter), width=6),
        dbc.Col(dcc.Graph(id="parallel-plot", figure=fig_parallel), width=6),
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            row_selectable="single",
            page_size=10,
            style_table={'overflowY': 'auto', 'height': '340px'},
            style_data_conditional=[],
        ), width=12)
    ])
])

# Callback: When either a scatter point is clicked or a row is selected in the data table,
# update the parallel coordinates plot and the scatter plot to highlight the corresponding data.
@app.callback(
    [Output("data-table", "selected_rows"),
     Output("data-table", "page_current"),
     Output("data-table", "style_data_conditional"),
     Output("parallel-plot", "figure"),
     Output("scatter-plot", "figure")],
    [Input("scatter-plot", "clickData"),
     Input("data-table", "selected_rows")],
    [State("parallel-plot", "figure"),
     State("scatter-plot", "figure")]
)
def update_selection(scatter_click, table_selected, parallel_fig, scatter_fig):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Determine the selected row index.
    if triggered_id == "scatter-plot" and scatter_click:
        selected_index = scatter_click["points"][0]["pointIndex"]
    elif triggered_id == "data-table" and table_selected:
        selected_index = table_selected[0]
    else:
        raise PreventUpdate

    # Get the corresponding ID from the DataFrame.
    selected_id = df.iloc[selected_index][id_column]
    page_number = selected_index // 10

    # Define conditional styling to highlight the selected row in the data table.
    if isinstance(selected_id, (int, float)):
        filter_query = f"{{{id_column}}} = {selected_id}"
    else:
        filter_query = f"{{{id_column}}} = '{selected_id}'"
    style_data_conditional = [{
        "if": {"filter_query": filter_query},
        "backgroundColor": "#FDE68A",
        "color": "black",
    }]

    # Update the parallel coordinates plot:
    label_to_col = {v: k for k, v in labels.items()}
    dimensions = parallel_fig["data"][0]["dimensions"]
    for dim in dimensions:
        orig_col = label_to_col.get(dim["label"], None)
        if orig_col is None:
            continue
        value = df.loc[selected_index, orig_col]
        try:
            value_float = float(value)
            delta = value_float / 100000 if value_float != 0 else 0.00001
            dim["constraintrange"] = [value_float - delta, value_float]
        except (ValueError, TypeError):
            dim["constraintrange"] = [value, value]

    # Update the scatter plot: set the selectedpoints property.
    scatter_fig["data"][0]["selectedpoints"] = [selected_index]

    return [selected_index], page_number, style_data_conditional, parallel_fig, scatter_fig

if __name__ == "__main__":
    app.run(debug=True)
