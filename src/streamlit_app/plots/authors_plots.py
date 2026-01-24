
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