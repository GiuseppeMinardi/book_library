from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_api_endpoint: AnyUrl = Field(default="http://localhost:8000", env="DB_API_ENDPOINT", description="The endpoint URL for the database API")