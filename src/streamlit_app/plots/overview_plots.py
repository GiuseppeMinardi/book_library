import pandas as pd
import plotly.express as px


def plot_authors(df: pd.DataFrame) -> px.bar:
    """Create a bar chart for most represented authors.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'name' and 'book_count'
    
    Returns
    -------
    px.bar
        Plotly bar chart figure
    """
    fig = px.bar(
        df,
        x="book_count",
        y="name",
        orientation="h",
        title="Top 10 Most Represented Authors",
        labels={"book_count": "Number of Books", "name": "Author"},
        color="book_count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(height=400, showlegend=False, yaxis_autorange="reversed")
    return fig


def plot_categories(df: pd.DataFrame) -> px.bar:
    """Create a bar chart for books by category.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns 'name' and 'count'
    
    Returns
    -------
    px.bar
        Plotly bar chart figure
    """
    fig = px.bar(
        df,
        x="count",
        y="name",
        orientation="h",
        title="Books by Category",
        labels={"count": "Number of Books", "name": "Category"},
        color="count",
        color_continuous_scale="Greens",
    )
    fig.update_layout(height=400, showlegend=False, yaxis_autorange="reversed")
    return fig