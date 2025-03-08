"""
Layout components for the Dash application.
"""

from dash import html, dcc, dash_table
from db_utils import queries, max_params

def create_sidebar_section(title: str, children: list) -> html.Div:
    """Create a styled sidebar section."""
    return html.Div(
        className='mb-6 bg-white rounded-lg shadow-sm p-4',
        children=[
            html.H4(title, className='text-lg font-semibold text-gray-800 mb-4'),
            *children
        ]
    )

def create_button(text: str, id: str, className: str = '') -> html.Button:
    """Create a styled button."""
    return html.Button(
        text,
        id=id,
        n_clicks=0,
        className=f'w-full px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 {className}'
    )

def create_input(id: dict, placeholder: str = '', className: str = '') -> dcc.Input:
    """Create a styled input."""
    return dcc.Input(
        id=id,
        type='text',
        className=f'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 {className}',
        placeholder=placeholder
    )

def create_layout() -> html.Div:
    """
    Create the main layout for the application.
    
    Returns:
        html.Div: The main application layout.
    """
    return html.Div([
        # Stores
        dcc.Store(id='last-query-store', data={'query': '', 'param_values': [],'query_name':''}),
        dcc.Store(id='dataframe-store', data=None),
        
        # Main Content
        html.Div(
            className='min-h-screen bg-gray-100',
            children=[
                # Navigation Bar
                html.Nav(
                    className='bg-white shadow-sm',
                    children=[
                        html.Div(
                            className='px-4',
                            children=[
                                html.Div(
                                    className='flex justify-between h-16',
                                    children=[
                                        html.Div(
                                            className='flex',
                                            children=[
                                                html.Div(
                                                    className='flex-shrink-0 flex items-center',
                                                    children=[
                                                        html.H1('Query Dashboard', className='text-xl font-bold text-gray-800')
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                
                # Content Container
                html.Div(
                    className='flex',
                    children=[
                        # Sidebar
                        html.Div(
                            className='w-80 min-h-screen bg-gray-50 shadow-sm p-6',
                            children=[
                                # Query Selection
                                create_sidebar_section(
                                    "Select Query",
                                    [
                                        dcc.Dropdown(
                                            id='query-selector',
                                            options=[{'label': k, 'value': k} for k in queries.keys()],
                                            placeholder='Select a query',
                                            className='mb-4'
                                        )
                                    ]
                                ),
                                
                                # Parameters
                                create_sidebar_section(
                                    "Parameters",
                                    [
                                        html.Div(
                                            id='parameter-inputs',
                                            children=[
                                                html.Div(
                                                    id={'type': 'param-div', 'index': i},
                                                    className='mb-4',
                                                    children=[
                                                        html.Label(
                                                            id={'type': 'param-label', 'index': i},
                                                            className='block text-sm font-medium text-gray-700 mb-1'
                                                        ),
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
                                                )
                                                for i in range(max_params)
                                            ]
                                        ),
                                        create_button('Run Query', 'run-query', 'mt-4')
                                    ]
                                ),
                                
                                # Analysis Tools
                                create_sidebar_section(
                                    "Analysis Tools",
                                    [
                                        html.Div(
                                            className='mb-4',
                                            children=[
                                                html.Label(
                                                    'Custom Report',
                                                    className='block text-sm font-medium text-gray-700 mb-1'
                                                ),
                                                create_button('Generate Report', 'run-report')
                                            ]
                                        ),
                                        html.Div(
                                            className='mb-4',
                                            children=[
                                                html.Label(
                                                    'YData Profiling',
                                                    className='block text-sm font-medium text-gray-700 mb-1'
                                                ),
                                                dcc.Checklist(
                                                    id='ydata-tsmode',
                                                    options=[{'label': 'Enable Timeseries Mode', 'value': 'tsmode'}],
                                                    value=[],
                                                    className='mb-2'
                                                ),
                                                create_button('Generate Profile', 'generate-profile')
                                            ]
                                        ),
                                        # Temporarily commenting out Sweetviz Report section
                                        # html.Div(
                                        #     className='mb-4',
                                        #     children=[
                                        #         html.Label(
                                        #             'Sweetviz Report',
                                        #             className='block text-sm font-medium text-gray-700 mb-1'
                                        #         ),
                                        #         create_button('Generate Sweetviz Report', 'generate-sweetviz')
                                        #     ]
                                        # )
                                    ]
                                ),
                                
                                # AI Tools
                                create_sidebar_section(
                                    "AI Tools",
                                    [
                                        html.Div(
                                            className='mb-4',
                                            children=[
                                                html.Label(
                                                    'VizroAI Description',
                                                    className='block text-sm font-medium text-gray-700 mb-1'
                                                ),
                                                dcc.Input(
                                                    id='user-input',
                                                    type='text',
                                                    placeholder='Enter your visualization description...',
                                                    className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 mb-2'
                                                ),
                                                create_button('Generate Plot', 'generate-plot')
                                            ]
                                        ),
                                        # Temporarily commenting out Pandas AI section
                                        # html.Div(
                                        #     className='mb-4',
                                        #     children=[
                                        #         html.Label(
                                        #             'Pandas AI Query',
                                        #             className='block text-sm font-medium text-gray-700 mb-1'
                                        #         ),
                                        #         dcc.Input(
                                        #             id='pandas-ai-input',
                                        #             type='text',
                                        #             placeholder='Enter your question...',
                                        #             className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 mb-2'
                                        #         ),
                                        #         create_button('Run Pandas AI', 'run-pandas-ai')
                                        #     ]
                                        # )
                                    ]
                                ),
                                
                                # Custom SQL
                                create_sidebar_section(
                                    "Custom SQL Query",
                                    [
                                        dcc.Textarea(
                                            id='custom-sql-input',
                                            placeholder='Enter your custom SQL query here...',
                                            className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 mb-2',
                                            style={'height': '100px'}
                                        ),
                                        create_button('Run Custom SQL', 'run-custom-sql')
                                    ]
                                )
                            ]
                        ),
                        
                        # Main Content Area
                        html.Div(
                            className='flex-1 p-8',
                            children=[
                                html.Div(
                                    className='bg-white rounded-lg shadow-sm p-6',
                                    children=[
                                        dcc.Tabs(
                                            id='tabs',
                                            value='data-tab',
                                            className='mb-4',
                                            children=[
                                                dcc.Tab(
                                                    label='Data',
                                                    value='data-tab',
                                                    className='p-4',
                                                    selected_className='border-b-2 border-indigo-500',
                                                    children=[
                                                        dash_table.DataTable(
                                                            id='query-results-table',
                                                            style_table={'overflowX': 'auto'},
                                                            style_cell={
                                                                'textAlign': 'left',
                                                                'padding': '12px 8px',
                                                                'font-size': '14px'
                                                            },
                                                            style_header={
                                                                'backgroundColor': '#f3f4f6',
                                                                'fontWeight': 'bold',
                                                                'border': 'none'
                                                            },
                                                            style_data={
                                                                'border': 'none',
                                                                'borderBottom': '1px solid #e5e7eb'
                                                            }
                                                        )
                                                    ]
                                                ),
                                                dcc.Tab(
                                                    label='Report',
                                                    value='report-tab',
                                                    className='p-4',
                                                    selected_className='border-b-2 border-indigo-500',
                                                    children=[html.Div(id='report-content')]
                                                ),
                                                dcc.Tab(
                                                    label='YData Profiling',
                                                    value='ydata-tab',
                                                    className='p-4',
                                                    selected_className='border-b-2 border-indigo-500',
                                                    children=[
                                                        html.Iframe(
                                                            id='ydata-profile',
                                                            style={'width': '100%', 'height': '800px', 'border': 'none'}
                                                        )
                                                    ]
                                                ),
                                                # Temporarily commenting out SweetViz tab
                                                # dcc.Tab(
                                                #     label='Sweetviz Profiling',
                                                #     value='sweetviz-tab',
                                                #     className='p-4',
                                                #     selected_className='border-b-2 border-indigo-500',
                                                #     children=[
                                                #         html.Iframe(
                                                #             id='sweetviz-profile',
                                                #             style={'width': '100%', 'height': '800px', 'border': 'none'}
                                                #         )
                                                #     ]
                                                # ),
                                                dcc.Tab(
                                                    label='VizroAI',
                                                    value='vizroai-tab',
                                                    className='p-4',
                                                    selected_className='border-b-2 border-indigo-500',
                                                    children=[
                                                        dcc.Graph(id='vizroai-plot'),
                                                        html.Pre(
                                                            id='vizroai-code',
                                                            className='mt-4 p-4 bg-gray-50 rounded-md font-mono text-sm'
                                                        ),
                                                        html.Pre(
                                                            id='vizroai-insights',
                                                            className='mt-4 p-4 bg-gray-50 rounded-md'
                                                        ),
                                                        html.Pre(
                                                            id='vizroai-explanation',
                                                            className='mt-4 p-4 bg-gray-50 rounded-md'
                                                        )
                                                    ]
                                                ),
                                                # Temporarily commenting out Pandas AI tab
                                                # dcc.Tab(
                                                #     label='Pandas AI',
                                                #     value='pandas-ai-tab',
                                                #     className='p-4',
                                                #     selected_className='border-b-2 border-indigo-500',
                                                #     children=[
                                                #         html.Pre(
                                                #             id='pandas-ai-response',
                                                #             className='p-4 bg-gray-50 rounded-md'
                                                #         )
                                                #     ]
                                                # )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]) 