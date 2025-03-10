"""
Layout components for the Dash application.
"""

from dash import html, dcc, dash_table
from db_utils import load_queries, get_params
from config import Config

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
        className=f'px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 {className}',
        style={
            'backgroundColor': '#2563eb',  # Explicit background color
            'color': 'white',              # Explicit text color
            'border': 'none',              # No border
            'cursor': 'pointer'            # Pointer cursor
        }
    )

def create_input(id: dict, placeholder: str = '', className: str = '') -> dcc.Input:
    """Create a styled input."""
    return dcc.Input(
        id=id,
        type='text',
        placeholder=placeholder,
        className=f'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 {className}',
        style={
            'backgroundColor': 'white',    # Explicit background color
            'color': 'black',              # Explicit text color
            'borderColor': '#d1d5db'       # Explicit border color
        }
    )

def create_layout(config: Config) -> html.Div:
    """
    Create the main application layout.
    
    Args:
        config (Config): The application configuration instance.
        
    Returns:
        html.Div: The main application layout.
    """
    # Load queries for this configuration
    queries_dict = load_queries(config)
    max_params = max(len(query['params']) for query in queries_dict.values()) if queries_dict else 0
    
    return html.Div(
        className='flex h-screen bg-gray-100',
        style={
            'backgroundColor': '#f3f4f6',  # Explicit background color
            'color': '#111827'             # Explicit text color
        },
        children=[
            # Stores for state management
            dcc.Store(id='last-query-store'),
            dcc.Store(id='dataframe-store'),
            
            # Main container
            html.Div(
                className='flex flex-col w-full',
                children=[
                    # Navigation bar
                    html.Nav(
                        className='bg-white shadow-sm',
                        style={
                            'backgroundColor': 'white',  # Explicit background color
                            'boxShadow': '0 1px 2px 0 rgba(0, 0, 0, 0.05)'  # Explicit shadow
                        },
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
                                                            html.H1(
                                                                'Query Dashboard', 
                                                                className='text-xl font-bold text-gray-800',
                                                                style={'color': '#1f2937'}  # Explicit text color
                                                            )
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
                                style={
                                    'backgroundColor': '#f9fafb',  # Explicit background color
                                    'boxShadow': '0 1px 2px 0 rgba(0, 0, 0, 0.05)'  # Explicit shadow
                                },
                                children=[
                                    # Query Selection
                                    create_sidebar_section(
                                        "Select Query",
                                        [
                                            dcc.Dropdown(
                                                id='query-selector',
                                                options=[{'label': k, 'value': k} for k in queries_dict.keys()],
                                                placeholder='Select a query...',
                                                className='mb-4',
                                                style={
                                                    'color': 'black',
                                                    'backgroundColor': 'white'
                                                },
                                                optionHeight=35
                                            ),
                                            html.Div(id='parameter-inputs', className='space-y-4'),
                                            create_button('Run Query', 'run-query', 'mt-4 w-full')
                                        ]
                                    ),
                                    
                                    # Custom SQL
                                    create_sidebar_section(
                                        "Custom SQL",
                                        [
                                            dcc.Textarea(
                                                id='custom-sql-input',
                                                placeholder='Enter custom SQL...',
                                                className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500',
                                                style={
                                                    'height': '150px',
                                                    'backgroundColor': 'white',
                                                    'color': 'black',
                                                    'borderColor': '#d1d5db'
                                                }
                                            ),
                                            create_button('Run Custom SQL', 'run-custom-sql', 'mt-4 w-full')
                                        ]
                                    ),
                                    
                                    # Reports
                                    create_sidebar_section(
                                        "Reports",
                                        [
                                            create_button('Generate Report', 'run-report', 'mb-2 w-full')
                                        ]
                                    ),
                                    
                                    # Data Profiling
                                    create_sidebar_section(
                                        "Data Profiling",
                                        [
                                            html.Div([
                                                html.Label(
                                                    'YData Profiling Options:', 
                                                    className='block mb-2',
                                                    style={'color': '#1f2937'}  # Explicit text color
                                                ),
                                                dcc.Checklist(
                                                    id='ydata-tsmode',
                                                    options=[
                                                        {'label': ' Time Series Mode', 'value': 'tsmode'}
                                                    ],
                                                    value=[],
                                                    className='mb-2',
                                                    style={
                                                        'color': '#1f2937',  # Explicit text color
                                                        'backgroundColor': 'transparent'
                                                    },
                                                    inputStyle={
                                                        'marginRight': '5px'
                                                    },
                                                    labelStyle={
                                                        'display': 'inline-block',
                                                        'marginRight': '15px',
                                                        'color': '#1f2937'
                                                    }
                                                ),
                                                create_button('Generate YData Profile', 'generate-profile', 'mb-2 w-full')
                                            ])
                                        ]
                                    ),
                                    
                                    # Vizro AI
                                    create_sidebar_section(
                                        "Vizro AI",
                                        [
                                            html.Label(
                                                'What would you like to visualize?', 
                                                className='block mb-2',
                                                style={'color': '#1f2937'}  # Explicit text color
                                            ),
                                            dcc.Textarea(
                                                id='user-input',
                                                placeholder='E.g., Show me a bar chart of sales by region',
                                                className='w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 mb-2',
                                                style={
                                                    'height': '80px',
                                                    'backgroundColor': 'white',
                                                    'color': 'black',
                                                    'borderColor': '#d1d5db'
                                                }
                                            ),
                                            create_button('Generate Plot', 'generate-plot', 'w-full')
                                        ]
                                    )
                                ]
                            ),
                            
                            # Main Content
                            html.Div(
                                className='flex-1 p-6',
                                children=[
                                    dcc.Tabs(
                                        id='tabs',
                                        value='data-tab',
                                        className='mb-4',
                                        style={
                                            'color': '#1f2937',
                                            'borderBottom': '1px solid #e5e7eb'
                                        },
                                        children=[
                                            dcc.Tab(
                                                label='Data',
                                                value='data-tab',
                                                className='py-2 px-4',
                                                selected_className='border-b-2 border-blue-500 text-blue-500',
                                                style={'backgroundColor': 'white', 'color': '#1f2937'},
                                                selected_style={'backgroundColor': 'white', 'color': '#3b82f6'},
                                                children=[
                                                    html.Div(
                                                        className='overflow-x-auto',
                                                        children=[
                                                            dash_table.DataTable(
                                                                id='query-results-table',
                                                                page_size=15,
                                                                style_table={'overflowX': 'auto'},
                                                                style_cell={
                                                                    'textAlign': 'left',
                                                                    'padding': '8px',
                                                                    'minWidth': '100px',
                                                                    'maxWidth': '300px',
                                                                    'whiteSpace': 'normal',
                                                                    'overflow': 'hidden',
                                                                    'textOverflow': 'ellipsis',
                                                                    'backgroundColor': 'white',
                                                                    'color': 'black'
                                                                },
                                                                style_header={
                                                                    'backgroundColor': 'rgb(240, 242, 245)',
                                                                    'fontWeight': 'bold',
                                                                    'border': '1px solid #e2e8f0',
                                                                    'color': '#1f2937'
                                                                },
                                                                style_data={
                                                                    'border': '1px solid #e2e8f0'
                                                                },
                                                                style_data_conditional=[
                                                                    {
                                                                        'if': {'row_index': 'odd'},
                                                                        'backgroundColor': 'rgb(248, 250, 252)'
                                                                    }
                                                                ],
                                                                export_format='csv'
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            dcc.Tab(
                                                label='Report',
                                                value='report-tab',
                                                className='py-2 px-4',
                                                selected_className='border-b-2 border-blue-500 text-blue-500',
                                                style={'backgroundColor': 'white', 'color': '#1f2937'},
                                                selected_style={'backgroundColor': 'white', 'color': '#3b82f6'},
                                                children=[
                                                    html.Div(id='report-content')
                                                ]
                                            ),
                                            dcc.Tab(
                                                label='YData Profiling',
                                                value='ydata-tab',
                                                className='py-2 px-4',
                                                selected_className='border-b-2 border-blue-500 text-blue-500',
                                                style={'backgroundColor': 'white', 'color': '#1f2937'},
                                                selected_style={'backgroundColor': 'white', 'color': '#3b82f6'},
                                                children=[
                                                    html.Iframe(
                                                        id='ydata-profile',
                                                        style={'width': '100%', 'height': 'calc(100vh - 200px)', 'border': 'none'}
                                                    )
                                                ]
                                            ),
                                            dcc.Tab(
                                                label='Vizro AI',
                                                value='vizroai-tab',
                                                className='py-2 px-4',
                                                selected_className='border-b-2 border-blue-500 text-blue-500',
                                                style={'backgroundColor': 'white', 'color': '#1f2937'},
                                                selected_style={'backgroundColor': 'white', 'color': '#3b82f6'},
                                                children=[
                                                    html.Div(
                                                        className='grid grid-cols-1 lg:grid-cols-2 gap-4',
                                                        children=[
                                                            html.Div(
                                                                className='bg-white p-4 rounded shadow',
                                                                style={'backgroundColor': 'white', 'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'},
                                                                children=[
                                                                    html.H3('Visualization', className='text-lg font-semibold mb-2', style={'color': '#1f2937'}),
                                                                    dcc.Graph(id='vizroai-plot', style={'height': '400px'})
                                                                ]
                                                            ),
                                                            html.Div(
                                                                className='bg-white p-4 rounded shadow',
                                                                style={'backgroundColor': 'white', 'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'},
                                                                children=[
                                                                    html.Div([
                                                                        html.H3('Code', className='text-lg font-semibold mb-2', style={'color': '#1f2937'}),
                                                                        html.Pre(
                                                                            id='vizroai-code',
                                                                            className='bg-gray-100 p-2 rounded text-sm overflow-auto',
                                                                            style={
                                                                                'maxHeight': '200px',
                                                                                'backgroundColor': '#f3f4f6',
                                                                                'color': '#1f2937'
                                                                            }
                                                                        )
                                                                    ]),
                                                                    html.Div([
                                                                        html.H3('Insights', className='text-lg font-semibold mb-2 mt-4', style={'color': '#1f2937'}),
                                                                        html.Pre(
                                                                            id='vizroai-insights',
                                                                            className='bg-gray-100 p-2 rounded text-sm overflow-auto',
                                                                            style={
                                                                                'maxHeight': '200px',
                                                                                'backgroundColor': '#f3f4f6',
                                                                                'color': '#1f2937'
                                                                            }
                                                                        )
                                                                    ]),
                                                                    html.Div([
                                                                        html.H3('Explanation', className='text-lg font-semibold mb-2 mt-4', style={'color': '#1f2937'}),
                                                                        html.Pre(
                                                                            id='vizroai-explanation',
                                                                            className='bg-gray-100 p-2 rounded text-sm overflow-auto',
                                                                            style={
                                                                                'maxHeight': '200px',
                                                                                'backgroundColor': '#f3f4f6',
                                                                                'color': '#1f2937'
                                                                            }
                                                                        )
                                                                    ])
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
                        ]
                    )
                ]
            )
        ]
    ) 