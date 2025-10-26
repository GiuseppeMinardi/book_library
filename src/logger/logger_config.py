"""
Logger configuration module.

This module provides the LoggerConfig class, which defines configuration
settings for the logger, including log level, log file paths, and console
logging options.
"""

from datetime import datetime
from pathlib import Path

from pydantic import DirectoryPath, Field
from pydantic_settings import BaseSettings


class LoggerConfig(BaseSettings):
    """
    Configuration settings for the logger.

    Attributes
    ----------
    log_level : str
        The logging level (e.g., DEBUG, INFO, WARNING, ERROR).
    logger_folder : DirectoryPath
        The directory where log files will be stored.
    log_file : FilePath
        The path to the log file, including the filename.
    enable_console_logging : bool
        Whether to enable logging to the console.
    """

    logger_name: str = Path(__file__).parents[2].name
    log_level: str = "INFO"
    logger_folder: DirectoryPath = Field(Path(__file__).parents[2].joinpath("logs"), description="Folder to store log files.")
    # log_file: Path = Field(default=logger_folder.joinpath(f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    enable_console_logging: bool = True

    @property
    def log_file(self) -> Path:
        """Construct the log file path with a timestamped filename."""
        self.logger_folder.mkdir(parents=True, exist_ok=True)
        return self.logger_folder.joinpath(f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

if __name__ == "__main__":
    c = LoggerConfig()
    print(c.model_dump_json(indent=4))