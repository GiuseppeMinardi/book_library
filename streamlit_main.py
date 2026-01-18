import streamlit as st

from src.database.db import Database
from src.models.project_paths import ProjectPathsSettings
from src.streamlit_app.stramlit_pages.overview import show_overview

project_paths = ProjectPathsSettings()


# Initialize database
@st.cache_resource
def get_database():
    """Initialize and return the Database instance."""
    return Database(db_location=project_paths.database_path)

# Sidebar navigation
st.sidebar.title("📚 Book Library")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "📖 Books", "✍️ Authors", "🏷️ Categories"]
)

db = get_database()

try:
    if page == "📊 Overview":
        show_overview(db)
    else:
        st.info("This page is under construction. Please check back later!")
except Exception as e:
    st.error(f"An error occurred: {e}")
    import traceback
    st.error(traceback.format_exc())