from src.models.project_paths import (
    DataFolderPathsSettings,
    ProjectPathsSettings,
    StreamlitAppPathsSettings,
    StreamlitQueryPathsSettings,
)


def test_data_folder_paths_settings():
    settings = DataFolderPathsSettings()
    
    assert settings.data_folder.name == "data"
    assert settings.isbn_response_folder.name == "isbn_response"


def test_streamlit_query_paths_settings():
    settings = StreamlitQueryPathsSettings()
    
    assert settings.root.name == "streamlit_queries"
    assert settings.overview_queries_folder.name == "overview"
    assert settings.books_queries_folder.name == "books"
    assert settings.authors_queries_folder.name == "authors"


def test_streamlit_app_paths_settings():
    settings = StreamlitAppPathsSettings()
    
    assert settings.streamlit_app_folder.name == "streamlit_app"
    assert isinstance(settings.streamlit_query_folder, StreamlitQueryPathsSettings)