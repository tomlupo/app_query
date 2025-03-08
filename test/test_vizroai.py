import vizro.plotly.express as px
from vizro_ai import VizroAI

vizro_ai = VizroAI()

df = px.data.gapminder()
fig = vizro_ai.plot(df, "describe life expectancy per continent over time")
fig.show()

res = vizro_ai.plot(df, "show me the geo distribution of life expectancy", return_elements=True)
print(res.code)
print(res.chart_insights)
print(res.code_explanation)

# Create user interface in plotly dash where user can provide user_input to vizro_ai.plot() and get the plot
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1('VizroAI Plot Interface'),
    dcc.Input(
        id='user-input',
        type='text',
        placeholder='Enter your description here...',
        style={'width': '50%'}
    ),
    html.Button('Submit', id='submit-button', n_clicks=0),
    dcc.Graph(id='output-graph'),
    html.Div(id='output-code', style={'whiteSpace': 'pre-line'}),
    html.Div(id='output-insights', style={'whiteSpace': 'pre-line'}),
    html.Div(id='output-explanation', style={'whiteSpace': 'pre-line'})
])

# Define the callback to update the graph
@app.callback(
    Output('output-graph', 'figure'),
    Output('output-code', 'children'),
    Output('output-insights', 'children'),
    Output('output-explanation', 'children'),
    Input('submit-button', 'n_clicks'),
    State('user-input', 'value')
)
def update_graph(n_clicks: int, user_input: str):
    """Update the graph based on user input.

    Args:
        n_clicks: Number of times the submit button has been clicked.
        user_input: User description for the desired visual.

    Returns:
        Updated figure, code, insights, and explanation.
    """
    if n_clicks > 0 and user_input:
        # Generate the plot using VizroAI
        res = vizro_ai.plot(df, user_input, return_elements=True)
        fig = res.get_fig_object(data_frame=df, vizro=False)
        code = f'Generated Code:\n{res.code}'
        insights = f'Chart Insights:\n{res.chart_insights}'
        explanation = f'Code Explanation:\n{res.code_explanation}'
        return fig, code, insights, explanation
    return {}, '', '', ''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

