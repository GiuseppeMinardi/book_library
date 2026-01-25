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

def plot_similarity_matrix_heatmap(similarity_matrix):
    """Plot a heatmap of the similarity matrix.

    Parameters
    ----------
    similarity_matrix : DataFrame
        DataFrame representing the similarity matrix.

    Returns
    -------
    Figure
        Plotly Figure object representing the heatmap.
    """
    fig = px.imshow(
        similarity_matrix,
        title="Books Similarity Matrix Heatmap",
        labels={"x": "Book 1", "y": "Book 2", "color": "Similarity"},
        color_continuous_scale="Viridis",
        zmin=0,
        zmax=1,
    )

    # Remove the tick labels (book names) from the axes
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    # Ensure the axis titles are still clean
    fig.update_layout(xaxis_title="Books", yaxis_title="Books")

    return fig


def plot_umap_scatter(books_df):
    """Plot a UMAP scatter plot of books.

    Parameters
    ----------
    books_df : DataFrame
        DataFrame containing UMAP coordinates and book metadata.

    Returns
    -------
    Figure
        Plotly Figure object representing the UMAP scatter plot.
    """
    fig = px.scatter(
        books_df,
        x="UMAP1",
        y="UMAP2",
        title="Books UMAP Scatter Plot",
        size=None,
        color="language",
        hover_data=[
            "title",
            "publishedYear",
        ],
    )
    fig.update_layout(xaxis_title="UMAP Dimension 1", yaxis_title="UMAP Dimension 2")
    return fig