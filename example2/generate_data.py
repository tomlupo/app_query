import pandas as pd
import sqlite3
from typing import List, Any

# Define a function to create a connection to the SQLite database
def create_connection(db_file: str) -> sqlite3.Connection:
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise

# Define a function to generate sample financial data
def generate_financial_data() -> List[pd.DataFrame]:
    """Generate three dataframes with up-to-date and extensive financial data."""
    # DataFrame 1: Stock Prices
    num_days = 365
    num_tickers = 5
    stock_prices = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=num_days * num_tickers, freq='D'),  # Generate data for a full year for each ticker
        'ticker': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'] * num_days,  # Repeat tickers to match the number of days
        'price': [round(150 + i * 0.5, 2) for i in range(num_days)] * num_tickers  # Simulate price changes over the year
    })

    # DataFrame 2: Company Financials
    num_entries = 100
    company_financials = pd.DataFrame({
        'ticker': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'] * (num_entries // num_tickers),  # Repeat tickers for more entries
        'revenue': [round(274.5 + i * 10, 2) for i in range(num_entries)],  # Simulate increasing revenue
        'profit': [round(57.4 + i * 2, 2) for i in range(num_entries)]  # Simulate increasing profit
    })

    # DataFrame 3: Market Indices
    num_indices = 3
    market_indices = pd.DataFrame({
        'index_name': ['S&P 500', 'NASDAQ', 'DOW JONES'] * (num_days + 1),  # Repeat indices for more entries
        'value': [round(4500 + i * 10, 2) for i in range((num_days + 1) * num_indices)],  # Simulate index value changes
        'date': pd.date_range(start='2024-01-01', periods=(num_days + 1) * num_indices, freq='D')  # Generate data for a full year
    })
    return [stock_prices, company_financials, market_indices]

# Define a function to store dataframes in a SQLite database
def store_dataframes_in_db(dataframes: List[pd.DataFrame], conn: sqlite3.Connection) -> None:
    """Store the given dataframes in the SQLite database."""
    table_names = ['stock_prices', 'company_financials', 'market_indices']
    for df, table_name in zip(dataframes, table_names):
        df.to_sql(table_name, conn, if_exists='replace', index=False)


# Main execution
if __name__ == '__main__':
    # Create a connection to the database
    conn = create_connection('sample_data.db')

    # Generate financial data
    dataframes = generate_financial_data()

    # Store dataframes in the database
    store_dataframes_in_db(dataframes, conn)

    # Close the database connection
    conn.close()
