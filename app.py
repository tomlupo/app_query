"""
Main application file for the risk analysis dashboard.

This is the entry point of the application. Users only need to provide the SOURCE parameter
to configure the database connection and queries.
"""

import sys
from dash import Dash
from config import init_config
from layouts import create_layout

def create_app(source: str = 'example') -> Dash:
    """
    Create and configure the Dash application.
    
    Args:
        source (str): The source module name to use for database connection and queries.
    
    Returns:
        Dash: The configured Dash application.
    """
    # Initialize configuration with the provided source
    init_config(source)
    
    # Initialize the app with external stylesheets for Tailwind CSS and custom styles
    app = Dash(
        __name__,
        external_stylesheets=[
            'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
            'https://cdn.jsdelivr.net/npm/@heroicons/v1/outline/index.min.css'
        ],
        suppress_callback_exceptions=True
    )
    
    # Set the layout
    app.layout = create_layout()
    
    # Import callbacks (this needs to happen after layout is set)
    import callbacks
    
    return app

def main():
    """Main entry point for the application."""
    # Get source from command line argument or use default
    source = sys.argv[1] if len(sys.argv) > 1 else 'example'
    
    # Create and run the app
    app = create_app(source)
    app.run(debug=True)

if __name__ == '__main__':
    main()