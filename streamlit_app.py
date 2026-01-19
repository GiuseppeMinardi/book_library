"""Book Library Streamlit Application.

This module provides a Streamlit-based dashboard for browsing and managing a book library.
It displays library overview statistics, books, authors, and categories with search and filtering capabilities.
"""

import streamlit as st

from src.database.db import Database
from src.models.project_paths import ProjectPathsSettings

project_paths = ProjectPathsSettings()


# Page config
st.set_page_config(page_title="📚 Book Library", layout="wide")


# Initialize database
@st.cache_resource
def get_database():
    """Get a cached Database instance."""
    return Database()


db = get_database()

# Sidebar navigation
st.sidebar.title("📚 Book Library")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "📖 Books", "✍️ Authors", "🏷️ Categories", "Edit Database"],
)

# Main content
if page == "📊 Overview":
    from src.streamlit_app.plots.overview_plots import plot_authors, plot_categories

    st.title("Library Overview")
    overview_queries_path = project_paths.streamlit_app_folder.streamlit_query_folder.overview_queries_folder
    with db:
        # Get summary statistics
        summary = db.run_query(
            overview_queries_path.joinpath("summary_statistics.sql").read_text(),
            as_dataframe=False,
        )

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
                st.metric(
                    "📄 Avg Pages", int(stats["avg_pages"]) if stats["avg_pages"] else 0
                )
            with col5:
                st.metric(
                    "📏 Max Pages", stats["max_pages"] if stats["max_pages"] else 0
                )

        st.divider()

        # Most prolific authors
        st.subheader("Top 10 Most Prolific Authors")
        authors_df = db.run_query(
            overview_queries_path.joinpath("most_represented_authors.sql").read_text(),
            as_dataframe=True,
        )

        if authors_df is not None and not authors_df.empty:
            fig_authors = plot_authors(authors_df)
            st.plotly_chart(fig_authors, use_container_width=True)
        else:
            st.info("No authors found in the database.")

        st.divider()

        # Books by category
        st.subheader("Books by Category")
        category_df = db.run_query(
            overview_queries_path.joinpath("books_by_category.sql").read_text(),
            as_dataframe=True,
        )
        if category_df is not None and not category_df.empty:
            fig_categories = plot_categories(category_df)
            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.info("No categories found in the database.")

elif page == "📖 Books":
    from src.streamlit_app.plots.books_plot import plot_language_barchart
    st.title("📖 Books")
    books_query_path = (
        project_paths.streamlit_app_folder.streamlit_query_folder.books_queries_folder
    )

    with db:
        # Build query
        books_query = books_query_path.joinpath("search_books.sql").read_text()
        params = []

        # Get books
        books_df = db.run_query(query=books_query, as_dataframe=True)
        
        st.subheader(f"Books ({len(books_df) if books_df is not None else 0})")
        
        if books_df is not None and not books_df.empty:
            st.dataframe(
                books_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "title": "Title",
                    "authors": "Authors",
                    "categories": "Categories",
                    "published_date": "Published Date",
                    "page_count": "Page Count",
                    "language": "Language",
                },
            )
        else:
            st.info("No books found matching your criteria.")

        st.divider()

        books_by_language_query = books_query_path.joinpath(
            "language_count.sql"
        ).read_text()

        language_df = db.run_query(query=books_by_language_query, as_dataframe=True)

        if language_df is not None and not language_df.empty:
            st.subheader("Books by Language")
            fig_language = plot_language_barchart(language_df=language_df)
            st.plotly_chart(figure_or_data=fig_language, use_container_width=True)
        else:
            st.info("No language data available.")

elif page == "✍️ Authors":
    from src.streamlit_app.plots.authors_plots import plot_nationalities_barchart
    st.title("✍️ Authors")

    with db:
        # Build query
        authors_query_folder = project_paths.streamlit_app_folder.streamlit_query_folder.authors_queries_folder
        query = authors_query_folder.joinpath("search_authors.sql").read_text()
        print(query)
        # Get authors
        authors_df = db.run_query(query, as_dataframe=True)
        print(f"Authors DataFrame:\n{authors_df}")
        
        st.subheader(f"Authors ({len(authors_df) if authors_df is not None else 0})")
        
        if authors_df is not None and not authors_df.empty:
            st.dataframe(authors_df, use_container_width=True, hide_index=True)
        else:
            st.info("No authors found matching your criteria.")

        st.subheader("Nationalities")
        if authors_df is not None and not authors_df.empty:
            fig_nationalities = plot_nationalities_barchart(authors_df)
            st.plotly_chart(fig_nationalities, use_container_width=True)
        else:
            st.info("No nationality data available.")

elif page == "🏷️ Categories":
    st.title("🏷️ Categories")
    categories_query_path = project_paths.streamlit_app_folder.streamlit_query_folder.categories_queries_folder
    
    with db:
        # Get categories with book counts
        categories_df = db.run_query(
            categories_query_path.joinpath("categories_count.sql").read_text(),
            as_dataframe=True,
        )
        
        if categories_df is not None and not categories_df.empty:
            # Show chart
            st.subheader(f"Categories ({len(categories_df)})")
            st.bar_chart(categories_df.set_index("name")["book_count"])
            
            # Show table
            st.dataframe(categories_df, use_container_width=True, hide_index=True)
        else:
            st.info("No categories found.")
elif page == "Edit Database":
    st.title("Edit Database")
    st.info("This feature is under development.")
    # in this section each table of the database will be editable through streamlit forms
    # For now, just show a placeholder

st.sidebar.divider()
st.sidebar.info("📚 Book Library Dashboard - Powered by Streamlit")
