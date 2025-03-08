"""
Database utilities module for handling SQL operations and query management.
"""

import os
import pandas as pd
from typing import Dict, List, Optional, Any
from config import config

def load_queries(directory: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Load SQL queries from files and extract their parameters.
    
    Args:
        directory (Optional[str]): Directory containing SQL files. Defaults to config.queries_path.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of queries and their parameters.
    """
    directory = directory or config.queries_path
    queries = {}
    param_pattern = config.query_param_pattern

    for filename in os.listdir(directory):
        if filename.endswith('.sql'):
            try:
                with open(os.path.join(directory, filename), 'r') as file:
                    query = file.read()

                    # Extract unique parameter names using a set
                    seen_params = set()
                    param_details = []
                    for match in param_pattern.finditer(query):
                        param_name = match.group(1)
                        if param_name not in seen_params:
                            seen_params.add(param_name)
                            param_type = 'date' if 'date' in param_name.lower() else 'text'
                            param_details.append({'name': param_name, 'type': param_type})

                    queries[filename] = {'query': query, 'params': param_details}

            except Exception as e:
                print(f'{filename} not loaded due to error: {e}')
    return queries

def execute_sql_query(query: str, params_dict: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Execute a SQL query and return the results as a DataFrame.
    
    Args:
        query (str): SQL query to execute.
        params_dict (Optional[Dict[str, Any]]): Dictionary of parameter names and values.
    
    Returns:
        pd.DataFrame: Query results as a DataFrame.
    """
    # Check if query is empty
    if not query:
        print("Query is None or empty.")
        return pd.DataFrame()

    # Modify query using params_dict
    if params_dict is None:
        params_dict = {}
    
    if config.query_param_replace_mode:
        for param, value in params_dict.items():
            query = query.replace(f"'{param}'", f"'{value}'")
        params = []
    else:
        params = [v for v in params_dict.values()]
        
    # Get connection
    conn = config.get_connection()
    
    # Execute query
    try:
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"An error occurred: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    
    return df

# Load queries at module initialization
queries = load_queries()
max_params = max(len(query['params']) for query in queries.values()) 