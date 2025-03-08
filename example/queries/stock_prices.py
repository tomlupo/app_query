import plotly.express as px

def create_report(df):

    fig = px.line(df, x='date', y='price', title='Stock Prices')

    return {'figure': fig,
            'data': df}