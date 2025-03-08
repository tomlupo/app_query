import sqlite3
import pandas as pd

def test_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('sample_data.db')
    
    try:
        # Example query to test the connection and data retrieval
        query = "SELECT * FROM market_indices"
        
        # Execute the query and fetch the results
        df = pd.read_sql_query(query, conn)
        
        # Print the results
        print("Query Results:")
        print(df)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

if __name__ == '__main__':
    test_database() 