from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleSheetSettings(BaseSettings):
    """Settings for the Google Books API.

    This class will read values from environment variables and a local
    `.env` file if present. Use the `GOOGLE_BOOKS_API_KEY` environment
    variable (note the corrected spelling).
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    sheet_id: str = Field(
        ...,
        alias="GOOGLE_SHEET_ID",
        description="Google Sheet ID for accessing the sheet.",
    )
    sheet_name: str = Field(
        default="ISBN", description="Name of the sheet within the Google Sheet"
    )
