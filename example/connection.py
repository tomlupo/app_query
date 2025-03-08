import sqlite3
import re

QUERY_PARAM_PATTERN = re.compile(r'(\w+)\s*(?:[=><!]+)\s*\?')
QUERY_PARAM_REPLACE_MODE = False
def get_connection():

    conn = sqlite3.connect('example/sample_data.db')
    
    return conn