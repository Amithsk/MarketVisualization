# components.py
import plotly.graph_objs as go
import pandas as pd


def plot_candles(df, date_col='Date', open_col='Open', high_col='High', low_col='Low', close_col='Close',
                 title="OHLC", overlays: list = None, height: int = 550):
    """
    overlays: list of dicts: {"label": "entry", "price": 123.45, "color": "green", "dash": "dash", "width":2}
    The function draws horizontal lines for each overlay at the given price.
    """
    fig = go.Figure(data=[go.Candlestick(
        x=df[date_col],
        open=df[open_col],
        high=df[high_col],
        low=df[low_col],
        close=df[close_col],
        name='OHLC'
    )])
    shapes = []
    annotations = []
    if overlays:
        for o in overlays:
            price = o.get("price")
            if price is None:
                continue
            label = o.get("label", "")
            dash = o.get("dash", "dash")
            width = o.get("width", 2)
            color = o.get("color", None)  # if None, rely on plotly default
            shapes.append({
                "type": "line",
                "xref": "paper",
                "x0": 0, "x1": 1,
                "y0": price, "y1": price,
                "line": {"color": color, "width": width, "dash": dash}
            })
            annotations.append({
                "x": 1.01, "xref": "paper",
                "y": price, "yref": "y",
                "text": f"{label}: {price}",
                "showarrow": False,
                "align": "left",
                "font": {"size": 11}
            })

    fig.update_layout(title=title, xaxis_rangeslider_visible=False, height=height,
                      shapes=shapes, annotations=annotations)
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

def bar_with_labels(df, x_col: str, y_col: str, title: str = None, text_format: str = ".2f", max_items: int = 30):
    """
    Vertical bar chart (Plotly) with values shown inside each bar.
    - df: DataFrame
    - x_col: category column (string)
    - y_col: numeric column to plot
    - text_format: python format spec (e.g. '.0f', '.2f')
    - max_items: show only top N items for readability
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title=title or "")
        return fig

    df_plot = df[[x_col, y_col]].dropna().copy()
    df_plot = df_plot.sort_values(by=y_col, ascending=False).head(max_items)

    # Ensure x is string for categorical axis
    df_plot[x_col] = df_plot[x_col].astype(str)
    y_vals = df_plot[y_col].astype(float)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_plot[x_col],
        y=y_vals,
        text=[format(v, text_format) for v in y_vals],
        textposition='inside',   # places values inside bars
        textfont=dict(size=12),
        hovertemplate=f"%{{x}}<br>{y_col}: %{{y:.2f}}<extra></extra>"
    ))
    fig.update_layout(
        title=title or "",
        xaxis_tickangle=-45,
        yaxis_title=y_col,
        margin=dict(l=40, r=20, t=50, b=120),
        height=600
    )
    return fig
def pie_split(labels, values, title=None):
    """
    Simple Plotly pie/donut chart. labels: list, values: list.
    """
    import plotly.graph_objs as go
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, textinfo='label+percent')])
    if title:
        fig.update_layout(title=title, height=420)
    return fig
