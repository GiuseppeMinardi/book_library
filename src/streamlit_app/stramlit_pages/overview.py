import streamlit as st

from ...database.db import Database
from ...models.project_paths import ProjectPathsSettings
from .plots.overview_plots import plot_authors, plot_categories

project_paths = ProjectPathsSettings()




def show_overview(db: Database):
    """Render the Overview page."""
    st.title("📚 Library Overview")
    
    overview_queries_path = project_paths.streamlit_app_folder.streamlit_query_folder.overview_queries_folder
    
    # Establish connection if not already connected
    if db.conn is None:
        db.connect()
    
    # Get summary statistics
    summary_statistics_query_path = overview_queries_path.joinpath("summary_statistics.sql")
    summary = db.run_query(summary_statistics_query_path.read_text(), as_dataframe=False)
    
    if summary:
        stats = summary[0]
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📖 Total Books", stats["total_books"])
        with col2:
            st.metric("✍️ Authors", stats["total_authors"])
        with col3:
            st.metric("🏷️ Categories", stats["total_categories"])
        with col4:
            st.metric("📄 Avg Pages", int(stats["avg_pages"]) if stats["avg_pages"] else 0)
        with col5:
            st.metric("📏 Max Pages", stats["max_pages"] if stats["max_pages"] else 0)
    
    st.divider()
    
    # Most represented authors
    most_represented_query_path = overview_queries_path.joinpath("most_represented_authors.sql")
    st.subheader("Top 10 Most Represented Authors")
    authors_df = db.run_query(most_represented_query_path.read_text(), as_dataframe=True)

    if authors_df is not None and not authors_df.empty:
        fig_authors = plot_authors(authors_df)
        st.plotly_chart(fig_authors, use_container_width=True)
        st.dataframe(authors_df, use_container_width=True, hide_index=True)
    else:
        st.info("No authors found in the database.")
    
    st.divider()
    
    # Books by category
    st.subheader("Books by Category")
    books_by_category_query_path = overview_queries_path.joinpath("books_by_category.sql")
    category_df = db.run_query(books_by_category_query_path.read_text(), as_dataframe=True)

    if category_df is not None and not category_df.empty:
        fig_categories = plot_categories(category_df)
        st.plotly_chart(fig_categories, use_container_width=True)