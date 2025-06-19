from dash import callback, callback_context
from dash.dependencies import Input, Output, State
import pandas as pd
from dash.exceptions import PreventUpdate
import plotly.express as px

# Import variables from legofit2 page.
from pages.legofit2 import df, id_column, labels, scatter_options, create_scatter_figure

# -------------------------------
# CALLBACK TO UPDATE for legofit2
# -------------------------------
@callback(
    [Output("data-table-legofit2", "selected_rows"),
     Output("data-table-legofit2", "page_current"),
     Output("data-table-legofit2", "style_data_conditional"),
     Output("parallel-plot-legofit2", "figure"),
     Output("scatter-plot-legofit2", "figure")],
    [Input("scatter-plot-legofit2", "clickData"),
     Input("scatter-plot-legofit2", "selectedData"),
     Input("parallel-plot-legofit2", "clickData"),
     Input("parallel-plot-legofit2", "selectedData"),
     Input("data-table-legofit2", "selected_rows"),
     Input("select-all-checkbox-legofit2", "value"),
     Input("parallel-plot-legofit2", "restyleData")],
    [State("parallel-plot-legofit2", "figure"),
     State("scatter-plot-legofit2", "figure"),
     State("data-table-legofit2", "derived_virtual_data"),
     State("data-table-legofit2", "data")]
)
def update_scatter_and_selection_legofit2(scatter_click, scatter_selected,
                                          parallel_click, parallel_selected, table_selected,
                                          checkbox_values, parallel_restyle, parallel_fig,
                                          scatter_fig, derived_virtual_data, original_data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    triggered_prop = ctx.triggered[0]["prop_id"]

    #for parallel coordinates range
    if "parallel-plot-legofit2.restyleData" in triggered_prop:
        label_to_col = {v: k for k, v in labels.items()}
        dimensions = parallel_fig["data"][0]["dimensions"]
        constraints_found = False
        selected_bool = pd.Series(True, index=df.index)
        for i, dim in enumerate(dimensions):
            if "constraintrange" in dim and dim["constraintrange"]:
                constraints_found = True
                orig_col = label_to_col.get(dim["label"])
                if orig_col is None:
                    continue
                cons = dim["constraintrange"]
                if isinstance(cons[0], list):
                    cons = cons[0]
                lower, upper = cons[0], cons[1]
                selected_bool &= df[orig_col].between(lower, upper)
        selected_indices = df.index[selected_bool].tolist() if constraints_found else []
        page_number = selected_indices[0] // 10 if selected_indices else 0
        style_data_conditional = []
        for idx in selected_indices:
            selected_id = df.iloc[idx][id_column]
            if isinstance(selected_id, (int, float)):
                filter_query = f"{{{id_column}}} = {selected_id}"
            else:
                filter_query = f"{{{id_column}}} = '{selected_id}'"
            style_data_conditional.append({
                "if": {"filter_query": filter_query},
                "backgroundColor": "#F39C12",
                "color": "white",
            })
        scatter_fig["data"][0]["selectedpoints"] = selected_indices
        clear_col4 = True
        if parallel_restyle and isinstance(parallel_restyle, list) and len(parallel_restyle) > 0:
            changes = parallel_restyle[0]
            if any("dimensions[3].constraintrange" in key for key in changes.keys()):
                clear_col4 = False
        for i, dim in enumerate(dimensions):
            if i == 3 and clear_col4:
                dim["constraintrange"] = None
        return selected_indices, page_number, style_data_conditional, parallel_fig, scatter_fig

    # for select-all checkbox
    if "select-all-checkbox-legofit2" in triggered_prop:
        if checkbox_values and "select_all" in checkbox_values:
            filtered_data = derived_virtual_data if derived_virtual_data is not None else original_data
            selected_indices = []
            for i, row in enumerate(original_data):
                if row in filtered_data:
                    selected_indices.append(i)
            page_number = selected_indices[0] // 10 if selected_indices else 0
            style_data_conditional = []
            for idx in selected_indices:
                selected_id = df.iloc[idx][id_column]
                if isinstance(selected_id, (int, float)):
                    filter_query = f"{{{id_column}}} = {selected_id}"
                else:
                    filter_query = f"{{{id_column}}} = '{selected_id}'"
                style_data_conditional.append({
                    "if": {"filter_query": filter_query},
                    "backgroundColor": "#F39C12",
                    "color": "white",
                })
            label_to_col = {v: k for k, v in labels.items()}
            dimensions = parallel_fig["data"][0]["dimensions"]
            for i, dim in enumerate(dimensions):
                if i == 3:
                    dim["constraintrange"] = None
                    continue
                orig_col = label_to_col.get(dim["label"], None)
                if orig_col is None:
                    continue
                values = df.iloc[selected_indices][orig_col]
                try:
                    numeric_values = values.astype(float)
                    ranges = []
                    for v in numeric_values:
                        delta = abs(v) / 100000 if v != 0 else 0.00001
                        ranges.append([v - delta, v + delta])
                    dim["constraintrange"] = ranges
                except Exception:
                    if not values.empty:
                        dim["constraintrange"] = [values.iloc[0], values.iloc[0]]
                    else:
                        dim["constraintrange"] = None
            scatter_fig["data"][0]["selectedpoints"] = selected_indices
            return selected_indices, page_number, style_data_conditional, parallel_fig, scatter_fig
        else:
            for dim in parallel_fig["data"][0]["dimensions"]:
                dim["constraintrange"] = None
            scatter_fig["data"][0]["selectedpoints"] = []
            return [], 0, [], parallel_fig, scatter_fig

    # Other selections
    selected_indices = None
    if "scatter-plot-legofit2.selectedData" in triggered_prop:
        if scatter_selected is None or not scatter_selected.get("points"):
            selected_indices = []
        else:
            selected_indices = [pt["pointIndex"] for pt in scatter_selected.get("points", [])]
    elif "scatter-plot-legofit2.clickData" in triggered_prop:
        if scatter_click is None or not scatter_click.get("points"):
            selected_indices = []
        else:
            selected_indices = [scatter_click["points"][0]["pointIndex"]]
    elif "parallel-plot-legofit2.selectedData" in triggered_prop:
        if parallel_selected is None or not parallel_selected.get("points"):
            selected_indices = []
        else:
            selected_indices = [pt["pointIndex"] for pt in parallel_selected.get("points", [])]
    elif "parallel-plot-legofit2.clickData" in triggered_prop:
        if parallel_click is None or not parallel_click.get("points"):
            selected_indices = []
        else:
            selected_indices = [parallel_click["points"][0]["pointIndex"]]
    elif "data-table-legofit2.selected_rows" in triggered_prop:
        selected_indices = table_selected if table_selected is not None else []
    else:
        selected_indices = []

    page_number = selected_indices[0] // 10 if selected_indices else 0
    style_data_conditional = []
    for idx in selected_indices:
        selected_id = df.iloc[idx][id_column]
        if isinstance(selected_id, (int, float)):
            filter_query = f"{{{id_column}}} = {selected_id}"
        else:
            filter_query = f"{{{id_column}}} = '{selected_id}'"
        style_data_conditional.append({
            "if": {"filter_query": filter_query},
            "backgroundColor": "#F39C12",
            "color": "white",
        })

    label_to_col = {v: k for k, v in labels.items()}
    dimensions = parallel_fig["data"][0]["dimensions"]
    for i, dim in enumerate(dimensions):
        if i == 3:
            dim["constraintrange"] = None
            continue
        orig_col = label_to_col.get(dim["label"], None)
        if orig_col is None:
            continue
        values = df.iloc[selected_indices][orig_col]
        try:
            numeric_values = values.astype(float)
            ranges = []
            for v in numeric_values:
                delta = abs(v) / 100000 if v != 0 else 0.00001
                ranges.append([v - delta, v + delta])
            dim["constraintrange"] = ranges
        except Exception:
            if not values.empty:
                dim["constraintrange"] = [values.iloc[0], values.iloc[0]]
            else:
                dim["constraintrange"] = None

    scatter_fig["data"][0]["selectedpoints"] = selected_indices

    return selected_indices, page_number, style_data_conditional, parallel_fig, scatter_fig

# -------------------------------
# CALLBACK TO FILTER DATATABLE DATA for legofit2
# -------------------------------
@callback(
    Output("data-table-legofit2", "data"),
    [Input("show-selected-checkbox-legofit2", "value"),
     Input("data-table-legofit2", "selected_rows")]
)
def update_table_data_legofit2(show_selected, selected_rows):
    if show_selected and "show_selected" in show_selected:
        if selected_rows:
            return df.iloc[selected_rows].to_dict("records")
        else:
            return []
    else:
        return df.to_dict("records")
