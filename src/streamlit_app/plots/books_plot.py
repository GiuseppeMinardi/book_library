"""plots for books module."""
import plotly.express as px


def plot_language_barchart(language_df):
    """Plot a bar chart of books by language.

    Parameters
    ----------
    language_df : DataFrame
        DataFrame containing language and book count.

    Returns
    -------
    Figure
        Plotly Figure object representing the bar chart.
    """
    fig = px.bar(
        language_df,
        x="language",
        y="book_count",
        title="Books by Language",
        labels={"language": "Language", "book_count": "Number of Books"},
    )
    fig.update_layout(xaxis_title="Language", yaxis_title="Number of Books")
    return fig
