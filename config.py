"""
Configuration module for the risk analysis application.

This module handles all configuration settings and imports required for the application.
"""

import os
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """
    Configuration class that manages application settings and dynamic imports.
    
    Args:
        source (str): The source module name to use for database connections and queries.
    """
    def __init__(self, source: str = 'example'):
        self.source = source
        self.queries_path = f'{source}/queries'
        self.reports_path = f'{source}/reports'
        self._load_source_config()
    
    def _load_source_config(self) -> None:
        """
        Loads configuration from the specified source module.
        """
        try:
            connection_module = importlib.import_module(f'{self.source}.connection')
            self.get_connection = getattr(connection_module, 'get_connection')
            self.query_param_pattern = getattr(connection_module, 'QUERY_PARAM_PATTERN')
            self.query_param_replace_mode = getattr(connection_module, 'QUERY_PARAM_REPLACE_MODE')
        except ImportError as e:
            raise ImportError(f'Failed to import source module {self.source}: {e}')
        except AttributeError as e:
            raise AttributeError(f'Required attribute missing in source module {self.source}: {e}')

# Default configuration
config = Config()

def init_config(source: str) -> None:
    """
    Initialize the configuration with a specific source.
    
    Args:
        source (str): The source module name to use.
    """
    global config
    config = Config(source) 