"""
Utility functions for data processing and component generation.
"""

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, dash_table
from typing import List, Union, Dict, Any

def unpack_to_dash(data: Any) -> List[Any]:
    """
    Recursively unpack data structures and convert them to Dash components.
    
    Args:
        data (Any): Data structure to convert to Dash components.
    
    Returns:
        List[Any]: List of Dash components.
    """
    components = []
    if isinstance(data, dict):
        for key, value in data.items():
            components.append(html.H5(key))
            components.extend(unpack_to_dash(value))
    elif isinstance(data, list):
        for item in data:
            components.extend(unpack_to_dash(item))
    elif isinstance(data, pd.DataFrame):
        components.append(dash_table.DataTable(
            data=data.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in data.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
            style_data={'border': '1px solid grey'}
        ))
    elif isinstance(data, go.Figure):
        components.append(dcc.Graph(figure=data))
    elif isinstance(data, str):
        components.append(dcc.Markdown(data))
    else:
        components.append(html.Div(str(data)))
    
    return components 