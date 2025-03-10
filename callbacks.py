"""
Callback functions for the Dash application.
"""

import time
import pandas as pd
from dash import Dash, Output, Input, State, callback_context, ALL, html, dcc
from ydata_profiling import ProfileReport
import sweetviz as sv
from vizro_ai import VizroAI
from db_utils import load_queries, get_params, execute_sql_query
from utils import unpack_to_dash
from config import Config
import importlib

# Initialize VizroAI globally since it's stateless
vizro_ai = VizroAI()

def create_parameter_input(param_details, index):
    """Create parameter input components."""
    param_name = param_details['name']
    param_type = param_details['type']
    
    return html.Div(
        id={'type': 'param-div', 'index': index},
        children=[
            html.Label(
                f'{param_name} ({param_type})',
                id={'type': 'param-label', 'index': index},
                className='form-label',
                style={
                    'display': 'block',
                    'marginBottom': '5px',
                    'fontWeight': '500',
                    'color': '#1f2937'  # Explicit text color
                }
            ),
            html.Div(
                id={'type': 'param-input-container', 'index': index},
                children=[
                    dcc.Input(
                        id={'type': 'param', 'index': index},
                        type='text',
                        className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500',
                        style={
                            'display': 'block' if param_type != 'date' else 'none',
                            'width': '100%',
                            'backgroundColor': 'white',
                            'color': 'black',
                            'borderColor': '#d1d5db'
                        }
                    ),
                    dcc.DatePickerSingle(
                        id={'type': 'param-date', 'index': index},
                        className='w-full',
                        style={
                            'display': 'block' if param_type == 'date' else 'none',
                            'zIndex': 9999,
                            'width': '100%'
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
        style={
            'display': 'block',
            'marginBottom': '15px'
        }
    )

def register_callbacks(app: Dash, config: Config) -> None:
    """
    Register all callbacks for the application.
    
    Args:
        app (Dash): The Dash application instance.
        config (Config): The application configuration instance.
    """
    # Load queries once at startup
    queries = load_queries(config)
    max_params = max(len(query['params']) for query in queries.values())
    
    @app.callback(
        Output('parameter-inputs', 'children'),
        Input('query-selector', 'value')
    )
    def update_parameters(selected_query):
        """Update parameter inputs based on selected query."""
        if not selected_query:
            return [html.Div(
                id={'type': 'param-div', 'index': i},
                style={'display': 'none'}
            ) for i in range(max_params)]
        
        # Get parameters for the selected query
        params = get_params(queries, selected_query)
        
        children = []
        for i in range(max_params):
            if i < len(params):
                children.append(create_parameter_input(params[i], i))
            else:
                children.append(html.Div(
                    id={'type': 'param-div', 'index': i},
                    style={'display': 'none'}
                ))
        return children

    @app.callback(
        Output('query-selector', 'options'),
        Input('query-selector', 'value')  # Dummy input to initialize
    )
    def update_query_options(_):
        """Update query selector options."""
        return [{'label': k, 'value': k} for k in queries.keys()]

    @app.callback(
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
    def run_queries(run_query_clicks, run_custom_sql_clicks, selected_query, 
                   text_values, date_values, custom_sql):
        """Execute SQL queries and update the results."""
        ctx = callback_context
        if not ctx.triggered:
            return [], [], {'query': '', 'params': []}, None, 'data-tab'

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        try:
            if button_id == 'run-query' and selected_query:
                # Get parameters for the selected query
                params = get_params(queries, selected_query)
                param_values = []
                for i, param in enumerate(params):
                    if param['type'] == 'date':
                        param_values.append(date_values[i])
                    else:
                        param_values.append(text_values[i])
                
                # Execute query with parameters
                df = execute_sql_query(selected_query, param_values, config, queries)
                
            elif button_id == 'run-custom-sql' and custom_sql:
                df = execute_sql_query(custom_sql, [], config, queries, is_file=False)
            else:
                return [], [], {'query': '', 'params': []}, None, 'data-tab'

            if df.empty:
                print("DataFrame is empty after query execution.")
                return [], [], {'query': '', 'params': []}, None, 'data-tab'

            data = df.to_dict('records')
            columns = [{'name': col, 'id': col} for col in df.columns]
            store_data = {
                'query': custom_sql if button_id == 'run-custom-sql' else selected_query,
                'params': [] if button_id == 'run-custom-sql' else param_values
            }
            
            return data, columns, store_data, df.to_json(), 'data-tab'
            
        except Exception as e:
            print(f"Query execution error: {e}")
            return [], [], {'query': '', 'params': []}, None, 'data-tab'

    @app.callback(
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
            return 'No data available for report.', 'report-tab'

        try:
            # Try to import query-specific report function
            query_name = selected_query.replace('.sql', '')
            report_data = None
            
            try:
                report_module = importlib.import_module(f'{config.source}.reports.{query_name}')
                if hasattr(report_module, 'create_report'):
                    report_data = report_module.create_report(df)
            except ImportError:
                print(f"No custom report module found for {query_name}")
            
            # Fallback to df.describe() if no custom report
            if report_data is None:
                report_data = df.describe().to_dict()
                
            report_content = unpack_to_dash(report_data)
            return report_content, 'report-tab'
        except Exception as e:
            print(f"Error generating report: {e}")
            return f"Error generating report: {str(e)}", 'report-tab'

    @app.callback(
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
            return '', 'ydata-tab'

        try:
            timestamp = int(time.time())
            tsmode = 'tsmode' in tsmode_values
            profile = ProfileReport(df, title="Pandas Profiling Report", tsmode=tsmode)
            profile_file = f"assets/ydata_profile_{timestamp}.html"
            profile.to_file(profile_file)
            return f"/assets/ydata_profile_{timestamp}.html", 'ydata-tab'
        except Exception as e:
            print(f"Error generating profile: {e}")
            return '', 'ydata-tab'

    @app.callback(
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
            return '', 'sweetviz-tab'

        try:
            timestamp = int(time.time())
            report = sv.analyze(df)
            report_file = f"assets/sweetviz_report_{timestamp}.html"
            report.show_html(filepath=report_file, open_browser=False)
            return f"/assets/sweetviz_report_{timestamp}.html", 'sweetviz-tab'
        except Exception as e:
            print(f"Error generating Sweetviz report: {e}")
            return '', 'sweetviz-tab'

    @app.callback(
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
            return {}, 'No data available for plot.', '', '', 'vizroai-tab'

        try:
            res = vizro_ai.plot(df, user_input, return_elements=True)
            fig = res.get_fig_object(data_frame=df, vizro=False)
            code = f'Generated Code:\n{res.code}'
            insights = f'Chart Insights:\n{res.chart_insights}'
            explanation = f'Code Explanation:\n{res.code_explanation}'
            return fig, code, insights, explanation, 'vizroai-tab'
        except Exception as e:
            print(f"Error generating plot: {e}")
            return {}, f"Error: {e}", '', '', 'vizroai-tab' 