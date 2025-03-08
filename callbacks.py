"""
Callback functions for the Dash application.
"""

import time
import pandas as pd
from dash import callback, Output, Input, State, callback_context, ALL, html, dcc
from ydata_profiling import ProfileReport
import sweetviz as sv
from vizro_ai import VizroAI
from db_utils import queries, execute_sql_query, max_params
from utils import unpack_to_dash
import importlib

# Initialize VizroAI
vizro_ai = VizroAI()

@callback(
    Output('parameter-inputs', 'children'),
    Input('query-selector', 'value')
)
def update_parameters(selected_query):
    """Update parameter inputs based on selected query."""
    if selected_query is None:
        return [html.Div(
            id={'type': 'param-div', 'index': i},
            children=[
                html.Label(id={'type': 'param-label', 'index': i}, className='form-label'),
                html.Div(
                    id={'type': 'param-input-container', 'index': i},
                    children=[
                        dcc.Input(
                            id={'type': 'param', 'index': i},
                            type='text',
                            className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500',
                            style={'display': 'none'}
                        ),
                        dcc.DatePickerSingle(
                            id={'type': 'param-date', 'index': i},
                            className='w-full',
                            style={
                                'display': 'none',
                                'zIndex': 9999
                            },
                            date=None,
                            display_format='YYYY-MM-DD',
                            placeholder='Select a date...',
                            clearable=True,
                            with_portal=True,
                            day_size=35
                        )
                    ]
                )
            ],
            style={'display': 'none'}
        ) for i in range(max_params)]

    param_details = queries[selected_query]['params']
    children = []
    for i in range(max_params):
        if i < len(param_details):
            param_name = param_details[i]['name']
            param_type = param_details[i]['type']
            children.append(html.Div(
                id={'type': 'param-div', 'index': i},
                children=[
                    html.Label(f'{param_name} ({param_type})', id={'type': 'param-label', 'index': i}, className='form-label'),
                    html.Div(
                        id={'type': 'param-input-container', 'index': i},
                        children=[
                            dcc.Input(
                                id={'type': 'param', 'index': i},
                                type='text',
                                className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500',
                                style={'display': 'block' if param_type != 'date' else 'none'}
                            ),
                            dcc.DatePickerSingle(
                                id={'type': 'param-date', 'index': i},
                                className='w-full',
                                style={
                                    'display': 'block' if param_type == 'date' else 'none',
                                    'zIndex': 9999
                                },
                                date=None,
                                display_format='YYYY-MM-DD',
                                placeholder='Select a date...',
                                clearable=True,
                                with_portal=True,
                                day_size=35
                            )
                        ]
                    )
                ],
                style={'display': 'block'}
            ))
        else:
            children.append(html.Div(
                id={'type': 'param-div', 'index': i},
                children=[
                    html.Label(id={'type': 'param-label', 'index': i}, className='form-label'),
                    html.Div(
                        id={'type': 'param-input-container', 'index': i},
                        children=[
                            dcc.Input(
                                id={'type': 'param', 'index': i},
                                type='text',
                                className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500',
                                style={'display': 'none'}
                            ),
                            dcc.DatePickerSingle(
                                id={'type': 'param-date', 'index': i},
                                className='w-full',
                                style={
                                    'display': 'none',
                                    'zIndex': 9999
                                },
                                date=None,
                                display_format='YYYY-MM-DD',
                                placeholder='Select a date...',
                                clearable=True,
                                with_portal=True,
                                day_size=35
                            )
                        ]
                    )
                ],
                style={'display': 'none'}
            ))
    return children

@callback(
    Output('query-results-table', 'data'),
    Output('query-results-table', 'columns'),
    Output('last-query-store', 'data'),
    Output('dataframe-store', 'data'),
    Output('tabs', 'value', allow_duplicate=True),
    Input('run-query', 'n_clicks'),
    Input('run-custom-sql', 'n_clicks'),
    State('query-selector', 'value'),
    State({'type': 'param', 'index': ALL}, 'value'),
    State({'type': 'param-date', 'index': ALL}, 'date'),
    State('custom-sql-input', 'value'),
    prevent_initial_call=True
)
def run_queries(run_query_clicks, run_custom_sql_clicks, selected_query, text_values, date_values, custom_sql):
    """Execute SQL queries and update the results."""
    ctx = callback_context
    if not ctx.triggered:
        return [], [], {'query': '', 'params': []}, None, 'data-tab'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'run-query' and selected_query:
        query = queries[selected_query]['query']
        # Combine text and date values based on parameter type
        param_values = []
        for i, param in enumerate(queries[selected_query]['params']):
            if param['type'] == 'date':
                param_values.append(date_values[i])
            else:
                param_values.append(text_values[i])
                
        params_dict = {param['name']: value for param, value in zip(queries[selected_query]['params'], param_values)}
        df = execute_sql_query(query, params_dict)
        if df.empty:
            print("DataFrame is empty after running the query.")
            return [], [], {'query': '', 'param_values': [],'query_name':''}, None, 'data-tab'

        data = df.to_dict('records')
        columns = [{'name': col, 'id': col} for col in df.columns]
        return data, columns, {'query': query, 'param_values': param_values,'query_name':selected_query}, data, 'data-tab'

    elif button_id == 'run-custom-sql' and custom_sql:
        df = execute_sql_query(custom_sql)
        if df.empty:
            print("DataFrame is empty after running the custom SQL.")
            return [], [], {'query': '', 'param_values': [],'query_name':''}, None, 'data-tab'

        data = df.to_dict('records')
        columns = [{'name': col, 'id': col} for col in df.columns]
        return data, columns, {'query': custom_sql, 'param_values': []}, data, 'data-tab'

    return [], [], {'query': '', 'param_values': [],'query_name':''}, None, 'data-tab'

@callback(
    Output('report-content', 'children'),
    Output('tabs', 'value', allow_duplicate=True),
    Input('run-report', 'n_clicks'),
    State('dataframe-store', 'data'),
    State('query-selector', 'value'),
    prevent_initial_call=True
)
def generate_report(run_report_clicks, df_data, selected_query):
    """Generate report from DataFrame."""
    if run_report_clicks == 0 or not df_data:
        return '', 'report-tab'

    df = pd.DataFrame.from_records(df_data)
    if df.empty:
        print("DataFrame is empty for report generation.")
        return 'No data available for report.', 'report-tab'

    try:
        # Try to import query-specific report function
        query_name = selected_query.replace('.sql', '')
        report_data = None
        
        try:
            report_module = importlib.import_module(f'{config.source}.reports.{query_name}')
            if hasattr(report_module, 'create_report'):
                report_data = report_module.create_report(df)
            else:
                print(f"No create_report function found in module for {query_name}")
        except ImportError:
            print(f"No custom report module found for {query_name}")
        
        # Fallback to df.describe() if no custom report is available
        if report_data is None:
            report_data = df.describe().to_dict()
            
        report_content = unpack_to_dash(report_data)
        return report_content, 'report-tab'
    except Exception as e:
        print(f"Error generating report: {e}")
        return f"Error generating report: {str(e)}", 'report-tab'

@callback(
    Output('ydata-profile', 'src'),
    Output('tabs', 'value', allow_duplicate=True),
    Input('generate-profile', 'n_clicks'),
    State('dataframe-store', 'data'),
    State('ydata-tsmode', 'value'),
    prevent_initial_call=True
)
def generate_ydata_profile(n_clicks, df_data, tsmode_values):
    """Generate YData profiling report."""
    if n_clicks == 0 or not df_data:
        return '', 'ydata-tab'

    df = pd.DataFrame.from_records(df_data)
    if df.empty:
        print("DataFrame is empty for YData profiling.")
        return '', 'ydata-tab'

    try:
        timestamp = int(time.time())
        tsmode = 'tsmode' in tsmode_values
        profile = ProfileReport(df, title="Pandas Profiling Report", tsmode=tsmode)
        profile_file = f"assets/ydata_profile_{timestamp}.html"
        profile.to_file(profile_file)
        return f"/assets/ydata_profile_{timestamp}.html", 'ydata-tab'
    except Exception as e:
        print(f"An error occurred while generating the profile: {e}")
        return '', 'ydata-tab'

@callback(
    Output('sweetviz-profile', 'src'),
    Output('tabs', 'value', allow_duplicate=True),
    Input('generate-sweetviz', 'n_clicks'),
    State('dataframe-store', 'data'),
    prevent_initial_call=True
)
def generate_sweetviz_report(n_clicks, df_data):
    """Generate Sweetviz profiling report."""
    if n_clicks == 0 or not df_data:
        return '', 'sweetviz-tab'

    df = pd.DataFrame.from_records(df_data)
    if df.empty:
        print("DataFrame is empty for Sweetviz profiling.")
        return '', 'sweetviz-tab'

    try:
        timestamp = int(time.time())
        report = sv.analyze(df)
        report_file = f"assets/sweetviz_report_{timestamp}.html"
        report.show_html(filepath=report_file, open_browser=False)
        return f"/assets/sweetviz_report_{timestamp}.html", 'sweetviz-tab'
    except Exception as e:
        print(f"An error occurred while generating the Sweetviz report: {e}")
        return '', 'sweetviz-tab'

@callback(
    Output('vizroai-plot', 'figure'),
    Output('vizroai-code', 'children'),
    Output('vizroai-insights', 'children'),
    Output('vizroai-explanation', 'children'),
    Output('tabs', 'value', allow_duplicate=True),
    Input('generate-plot', 'n_clicks'),
    State('dataframe-store', 'data'),
    State('user-input', 'value'),
    prevent_initial_call=True
)
def generate_vizroai_plot(n_clicks, df_data, user_input):
    """Generate plot using VizroAI."""
    if n_clicks == 0 or not df_data:
        return {}, '', '', '', 'vizroai-tab'

    df = pd.DataFrame.from_records(df_data)
    if df.empty:
        print("DataFrame is empty for VizroAI plot generation.")
        return {}, 'No data available for plot.', '', '', 'vizroai-tab'

    try:
        res = vizro_ai.plot(df, user_input, return_elements=True)
        fig = res.get_fig_object(data_frame=df, vizro=False)
        code = f'Generated Code:\n{res.code}'
        insights = f'Chart Insights:\n{res.chart_insights}'
        explanation = f'Code Explanation:\n{res.code_explanation}'
        return fig, code, insights, explanation, 'vizroai-tab'
    except Exception as e:
        print(f"An error occurred while generating the plot: {e}")
        return {}, f"An error occurred: {e}", '', '', 'vizroai-tab'

@callback(
    Output('pandas-ai-response', 'children'),
    Output('tabs', 'value', allow_duplicate=True),
    Input('run-pandas-ai', 'n_clicks'),
    State('dataframe-store', 'data'),
    State('pandas-ai-input', 'value'),
    prevent_initial_call=True
)
def run_pandas_ai(n_clicks, df_data, pandas_ai_input):
    """Generate response using Pandas AI."""
    if n_clicks == 0 or not df_data:
        return '', 'pandas-ai-tab'

    df = pd.DataFrame.from_records(df_data)
    if df.empty:
        print("DataFrame is empty for Pandas AI processing.")
        return 'No data available for Pandas AI.', 'pandas-ai-tab'

    try:
        df_smart = SmartDataframe(df, config={"llm": llm})
        response = df_smart.chat(pandas_ai_input)
        return response, 'pandas-ai-tab'
    except Exception as e:
        print(f"An error occurred while processing Pandas AI: {e}")
        return f"An error occurred: {e}", 'pandas-ai-tab' 