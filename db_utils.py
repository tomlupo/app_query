"""
Database utilities module for handling SQL operations and query management.
"""

import os
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from config import Config

def load_queries(config: Config) -> Dict[str, Dict[str, Any]]:
    """
    Load SQL queries from files and extract their parameters.
    
    Args:
        config (Config): Configuration instance containing paths and settings.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of queries and their parameters.
    """
    queries = {}
    param_pattern = config.query_param_pattern

    for filename in os.listdir(config.queries_path):
        if filename.endswith('.sql'):
            try:
                with open(os.path.join(config.queries_path, filename), 'r') as file:
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

def get_params(queries: Dict[str, Dict[str, Any]], query_name: str) -> List[Dict[str, str]]:
    """
    Get parameters for a specific query.
    
    Args:
        queries (Dict[str, Dict[str, Any]]): Dictionary of loaded queries.
        query_name (str): Name of the query file.
        
    Returns:
        List[Dict[str, str]]: List of parameter details.
    """
    return queries[query_name]['params'] if query_name in queries else []

def execute_sql_query(
    query: str, 
    params: Union[List[Any], Dict[str, Any]], 
    config: Config,
    queries: Dict[str, Dict[str, Any]],
    is_file: bool = True
) -> pd.DataFrame:
    """
    Execute a SQL query and return the results as a DataFrame.
    
    Args:
        query (str): SQL query to execute or query filename.
        params (Union[List[Any], Dict[str, Any]]): Query parameters as list or dict.
        config (Config): Configuration instance for database connection.
        queries (Dict[str, Dict[str, Any]]): Dictionary of loaded queries.
        is_file (bool): Whether query is a filename (True) or SQL string (False).
    
    Returns:
        pd.DataFrame: Query results as a DataFrame.
    """
    # Check if query is empty
    if not query:
        print("Query is None or empty.")
        return pd.DataFrame()

    # Get query from file if needed
    if is_file:
        if query not in queries:
            print(f"Query file {query} not found.")
            return pd.DataFrame()
        query = queries[query]['query']

    # Convert params to appropriate format
    if isinstance(params, dict):
        if config.query_param_replace_mode:
            for param, value in params.items():
                query = query.replace(f"'{param}'", f"'{value}'")
            params = []
        else:
            params = list(params.values())
    
    # Get connection
    conn = config.get_connection()
    
    # Execute query
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Query execution error: {e}")
        return pd.DataFrame()
    finally:
        conn.close() 