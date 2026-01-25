"""Module for generating plots related to authors using Plotly."""

import pandas as pd
import plotly.express as px


def plot_nationalities_barchart(authors_df: pd.DataFrame):
    """Plot a bar chart of authors by nationality."""
    nationality_count = authors_df.groupby("nationality", observed=True).size().reset_index(name="author_count")

    fig = px.bar(
        nationality_count,
        x="nationality",
        y="author_count",
        title="Authors by Nationality",
    )

    return fig


def plot_authors_similarity_matrix_heatmap(similarity_matrix):
    """Plot a heatmap of authors similarity matrix.

    Parameters
    ----------
    similarity_matrix : 2D array-like
        A square matrix representing similarity scores between authors.

    Returns
    -------
    Figure
        Plotly Figure object representing the heatmap.
    """
    fig = px.imshow(
        similarity_matrix,
        title="Authors Similarity Matrix Heatmap",
        labels={"x": "Author 1", "y": "Author 2", "color": "Similarity"},
        color_continuous_scale="Viridis",
        zmin=0,
        zmax=1,
    )

    # Remove the tick labels (book names) from the axes
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    # Ensure the axis titles are still clean
    fig.update_layout(xaxis_title="Authors", yaxis_title="Authors")

    return fig


def plot_authors_umap_scatter(authors_df: pd.DataFrame):
    """Plot a UMAP scatter plot of authors.

    Parameters
    ----------
    authors_df : DataFrame
        DataFrame containing UMAP coordinates and author metadata.

    Returns
    -------
    Figure
        Plotly Figure object representing the UMAP scatter plot.
    """
    fig = px.scatter(
        authors_df,
        x="UMAP1",
        y="UMAP2",
        title="Authors UMAP Scatter Plot",
        size=None,
        color="nationality",
        hover_data=[
            "name",
            "birth_date",
            "sex",
        ],
    )
    fig.update_layout(xaxis_title="UMAP Dimension 1", yaxis_title="UMAP Dimension 2")
    return fig
