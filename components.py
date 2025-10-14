# components.py
import plotly.graph_objs as go
import pandas as pd

def plot_candles(df, date_col='Date', open_col='Open', high_col='High', low_col='Low', close_col='Close', title="OHLC"):
    fig = go.Figure(data=[go.Candlestick(
        x=df[date_col],
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col],
        name='OHLC'
    )])
    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=550)
    return fig

def line_series(df, x_col, y_col, title=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines', name=y_col))
    if title:
        fig.update_layout(title=title)
    return fig

def simple_bar(df, x_col, y_col, title=None):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], name=y_col))
    if title:
        fig.update_layout(title=title)
    return fig
