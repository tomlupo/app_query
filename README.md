# Query Dashboard

A modular Dash application for analyzing data through SQL queries with various visualization and analysis tools.

## Features

- SQL query execution with parameter support
- Dynamic report generation with custom reporting capabilities
- YData profiling for detailed data analysis
- VizroAI visualization using natural language
- Custom SQL query support
- Automatic date picker for date parameters
- Flexible parameter pattern matching

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- dash
- pandas
- ydata-profiling
- vizro-ai
- python-dotenv

## Quick Start

1. Create your source module following the structure below
2. Run the application using one of these methods:

Using the batch file (Windows):
```bash
# Run with default source
run.bat

# Run with specific source
run.bat your_source_name
```

Using Python directly:
```bash
python app.py [source_module_name]
```
If no source module is specified, it defaults to 'example'.

## Project Structure

```
your_source/
├── connection.py      # Database connection and query configuration
├── queries/          # SQL query files
│   └── your_query.sql
└── reports/          # Custom report modules
    └── your_query.py # (same name as SQL file without .sql extension)
```

## Configuration

### Database Connection (`connection.py`)
```python
import re

# Required: Pattern for extracting parameters from SQL queries
# Default pattern matches: column_name = ?
# Extended pattern matches: column_name > ?, column_name < ?, etc.
QUERY_PARAM_PATTERN = re.compile(r'(\w+)\s*(?:[=><!]+)\s*\?')

# Required: Whether to replace parameters in SQL query
QUERY_PARAM_REPLACE_MODE = False

# Required: Database connection function
def get_connection():
    # Implement your database connection logic
    return your_connection
```

### SQL Queries
- Place your SQL files in `your_source/queries/`
- Use parameterized queries with the format matching your `QUERY_PARAM_PATTERN`
- Parameters containing 'date' in their name will automatically get a date picker

Example:
```sql
-- your_source/queries/sales_report.sql
SELECT * FROM sales 
WHERE revenue > ? 
AND transaction_date > ?;
```

### Custom Reports
Create custom report modules in `your_source/reports/` to generate specialized reports for specific queries.

1. Create a Python file with the same name as your SQL file (without .sql extension)
2. Implement a `create_report` function that takes a pandas DataFrame as input

Example:
```python
# your_source/reports/sales_report.py

def create_report(df):
    """
    Create a custom report from the query results.
    
    Args:
        df (pd.DataFrame): The query results as a DataFrame
    
    Returns:
        dict: A dictionary that will be unpacked into Dash components
    """
    return {
        'summary': df.describe().to_dict(),
        'custom_stats': {
            'total_revenue': df['revenue'].sum(),
            'average_transaction': df['revenue'].mean()
        }
    }
```

## Report Generation Logic

1. When "Generate Report" is clicked, the system:
   - Takes the current query name (e.g., "sales_report.sql")
   - Looks for a matching report module (e.g., "sales_report.py")
   - Tries to use its `create_report` function

2. Fallback behavior:
   - If no matching report module exists → uses `df.describe()`
   - If module exists but no `create_report` function → uses `df.describe()`
   - If any error occurs during report generation → shows error message

3. Report Data Format:
   - Return a dictionary from `create_report`
   - The dictionary will be unpacked into Dash components
   - Nested dictionaries become nested divs
   - Lists become bullet points
   - DataFrames/Series are converted to tables

## Additional Features

- **YData Profiling**: Generate detailed data profiling reports
- **VizroAI**: Create visualizations using natural language descriptions
- **Custom SQL**: Run ad-hoc SQL queries directly

## Usage

1. Select a query from the dropdown
2. Fill in any required parameters
3. Click "Run Query" to execute
4. Use the various tools in the sidebar to analyze the results:
   - Generate Report: Custom or basic statistics
   - YData Profiling: Detailed data analysis
   - VizroAI: AI-powered visualizations 

## Development

To add a new feature:

1. Update the relevant module
2. Add any new dependencies to requirements.txt
3. Update documentation if necessary

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT 