"""
Main application file for the risk analysis dashboard.

This is the entry point of the application. Users only need to provide the SOURCE parameter
to configure the database connection and queries.
"""

import sys
from typing import Optional
from dash import Dash
from config import init_config, Config
from layouts import create_layout
from callbacks import register_callbacks

def create_app(source: str = 'example') -> Dash:
    """
    Create and configure the Dash application.
    
    Args:
        source (str): The source module name to use for database connection and queries.
            Must be a valid source configuration name.
    
    Returns:
        Dash: The configured Dash application.
        
    Raises:
        ValueError: If source configuration cannot be initialized.
    """
    # Initialize configuration first
    try:
        config = init_config(source)
        print(f"Configuration initialized with source: {source}")
        print(f"Queries path: {config.queries_path}")
    except Exception as e:
        raise ValueError(f'Failed to initialize configuration for source {source}: {str(e)}')

    # Initialize the app with external stylesheets
    app = Dash(
        __name__,
        external_stylesheets=[
            'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
            'https://cdn.jsdelivr.net/npm/@heroicons/v1/outline/index.min.css'
        ],
        suppress_callback_exceptions=True
    )
    
    # Create layout with configuration
    app.layout = create_layout(config)
    
    # Register callbacks with app and configuration
    register_callbacks(app, config)
    
    return app

def main(source: Optional[str] = None) -> None:
    """
    Main entry point for the application.
    
    Args:
        source (Optional[str]): The source parameter. If None, will attempt to get from
            command line arguments. Defaults to 'example' if not provided.
            
    Raises:
        SystemExit: If configuration cannot be initialized or app creation fails.
    """
    try:
        # Get source from command line argument or use default
        if source is None:
            source = sys.argv[1] if len(sys.argv) > 1 else 'example'
            
        print(f'Initializing app with source: {source}')
        
        # Create and run the app
        app = create_app(source)
        app.run(debug=True)
        
    except ValueError as e:
        print(f'Configuration error: {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Unexpected error: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()