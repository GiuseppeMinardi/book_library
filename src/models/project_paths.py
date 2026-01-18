from pathlib import Path

from pydantic import DirectoryPath, Field
from pydantic_settings import BaseSettings


class DataFolderPathsSettings(BaseSettings):
    data_folder: DirectoryPath = Field(
        default=Path(__file__).parents[2].joinpath("data").resolve(),
        alias="DATA_FOLDER_PATH",
        description="Path to the data folder.",
    )

    @property
    def isbn_response_folder(self) -> Path:
        """Path to the ISBN response folder.
        
        Returns
        -------
        Path
            The path to the folder containing ISBN API responses.
        """
        return self.data_folder.joinpath("isbn_response")

class StreamlitQueryPathsSettings(BaseSettings):
    """Settings for Streamlit query folder paths.
    
    This class manages the configuration of paths related to Streamlit query
    folders, including overview, books, and authors query folders.
    """

    root: DirectoryPath = Field(
        default=Path(__file__).parents[1].joinpath("streamlit_app", "streamlit_queries").resolve(),
        description="Path to the root folder for Streamlit queries.",
    )

    @property
    def overview_queries_folder(self) -> Path:
        """Path to the Overview queries folder.
        
        Returns
        -------
        Path
            The path to the Overview queries folder.
        """
        return self.root.joinpath("overview").resolve()
    
    @property
    def books_queries_folder(self) -> Path:
        """Path to the Books queries folder.
        
        Returns
        -------
        Path
            The path to the Books queries folder.
        """
        return self.root.joinpath("books").resolve()
    
    @property
    def authors_queries_folder(self) -> Path:
        """Path to the Authors queries folder.
        
        Returns
        -------
        Path
            The path to the Authors queries folder.
        """
        return self.root.joinpath("authors").resolve()

class StreamlitAppPathsSettings(BaseSettings):
    """Settings for Streamlit application folder paths.
    
    This class manages the configuration of paths related to the Streamlit
    application, including the main application folder and query folders.
    """

    streamlit_app_folder: Path = Field(
        default=Path(__file__).parents[2].joinpath("streamlit_app"),
        alias="STREAMLIT_APP_FOLDER_PATH",
        description="Path to the Streamlit application folder.",
    )

    streamlit_query_folder: StreamlitQueryPathsSettings = Field(
        default_factory=StreamlitQueryPathsSettings,
        description="Settings for Streamlit query folder paths.",
    )

class ProjectPathsSettings(BaseSettings):
    """Settings for project paths.
    
    This class manages the configuration of project-level paths including
    the database path and data folder settings.
    """

    database_path: Path = Field(
        default=Path(__file__).parents[2].joinpath("data", "books.db"),
        alias="DATABASE_PATH",
        description="Path to the SQLite database file.",
    )
    data_folders: DataFolderPathsSettings = Field(
        default_factory=DataFolderPathsSettings,
        description="Settings for various data folder paths.",
    )
    streamlit_app_folder: StreamlitAppPathsSettings = Field(
        default_factory=StreamlitAppPathsSettings,
        description="Settings for Streamlit application folder paths.",
    )
