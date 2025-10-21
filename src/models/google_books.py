from typing import List, Optional

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleBooksSettings(BaseSettings):
    """Settings for the Google Books API.

    This class will read values from environment variables and a local
    `.env` file if present. Use the `GOOGLE_BOOKS_API_KEY` environment
    variable (note the corrected spelling).
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_key: SecretStr = Field(
        ...,
        alias="GOOLGE_BOOKS_API_KEY",
        description="API key for accessing the Google Books API",
    )

    base_url: str = Field(
        default="https://www.googleapis.com/books/v1/volumes",
        description="Base URL for the Google Books API",
    )


class IndustryIdentifier(BaseModel):
    type: str = Field(
        ..., description="Type of industry identifier (e.g., ISBN_13, ISBN_10)."
    )
    identifier: str = Field(
        ..., description="The identifier value associated with the type."
    )


class ImageLinks(BaseModel):
    smallThumbnail: Optional[str] = Field(
        None, description="URL for the small thumbnail image of the book cover."
    )
    thumbnail: Optional[str] = Field(
        None, description="URL for the standard thumbnail image of the book cover."
    )


class VolumeInfo(BaseModel):
    title: str = Field(..., description="The title of the book.")
    authors: Optional[List[str]] = Field(
        None, description="List of authors of the book."
    )
    publisher: Optional[str] = Field(None, description="The publisher of the book.")
    publishedDate: Optional[str] = Field(
        None, description="Date of publication (ISO 8601 format)."
    )
    description: Optional[str] = Field(
        None, description="Summary or description of the book."
    )
    industryIdentifiers: Optional[List[IndustryIdentifier]] = Field(
        None, description="Industry standard identifiers like ISBN."
    )
    pageCount: Optional[int] = Field(
        None, description="Total number of pages in the book."
    )
    printType: Optional[str] = Field(
        None, description="Type of printed material (e.g., BOOK, MAGAZINE)."
    )
    categories: Optional[List[str]] = Field(
        None, description="Book categories or genres."
    )
    maturityRating: Optional[str] = Field(
        None, description="Book maturity rating (e.g., NOT_MATURE)."
    )
    contentVersion: Optional[str] = Field(
        None, description="Content version tag for the book."
    )
    imageLinks: Optional[ImageLinks] = Field(None, description="Links to cover images.")
    language: Optional[str] = Field(
        None, description="Language code of the book (ISO 639-1)."
    )
    infoLink: Optional[str] = Field(
        None, description="URL for additional book information."
    )


class GoogleBooksResponse(BaseModel):
    kind: str = Field(..., description="The resource type (usually 'books#volume').")
    id_: str = Field(
        ..., alias="id", description="Unique identifier for the book volume."
    )
    etag: str = Field(..., description="ETag of the item for version control.")
    selfLink: str = Field(..., description="API link for the item resource.")
    volumeInfo: VolumeInfo = Field(
        ..., description="Metadata and descriptive info about the volume."
    )


class GoogleBookSlimResponse(BaseModel):
    """A slimmed-down representation of a Google Books API response.

    This class provides a subset of fields from the full Google Books API response,
    focusing on key metadata about a book.

    Attributes
    ----------
    kind : Optional[str]
        The resource type (e.g., 'books#volume').
    title : Optional[str]
        The title of the book.
    authors : Optional[list[str]]
        List of authors of the book.
    publisher : Optional[str]
        The publisher of the book.
    published_date : Optional[str]
        Date of publication (ISO 8601 format).
    description : Optional[str]
        Summary or description of the book.
    page_count : Optional[str]
        Total number of pages in the book.
    categories : Optional[list[str]]
        Book categories or genres.
    print_type : Optional[str]
        Type of printed material (e.g., BOOK, MAGAZINE).
    language : Optional[str]
        Language code of the book (ISO 639-1).
    info_link : Optional[str]
        URL for additional book information.
    small_thumbnail : Optional[str]
        URL for the small thumbnail image of the book cover.
    """

    kind: Optional[str] = Field(
        alias="kind", description="The resource type (e.g., 'books#volume')."
    )
    title: Optional[str] = Field(alias="title", description="The title of the book.")
    authors: Optional[list[str]] = Field(
        alias="authors", description="List of authors of the book."
    )
    publisher: Optional[str] = Field(
        alias="publisher", description="The publisher of the book."
    )
    published_date: Optional[str] = Field(
        alias="publishedDate", description="Date of publication (ISO 8601 format)."
    )
    description: Optional[str] = Field(
        alias="description", description="Summary or description of the book."
    )
    page_count: Optional[int] = Field(
        alias="pageCount", description="Total number of pages in the book."
    )
    categories: Optional[list[str]] = Field(
        alias="categories", description="Book categories or genres."
    )
    print_type: Optional[str] = Field(
        alias="printType",
        description="Type of printed material (e.g., BOOK, MAGAZINE).",
    )
    language: Optional[str] = Field(
        alias="language", description="Language code of the book (ISO 639-1)."
    )
    info_link: Optional[str] = Field(
        alias="infoLink", description="URL for additional book information."
    )
    small_thumbnail: Optional[str] = Field(
        alias="smallThumbnail",
        description="URL for the small thumbnail image of the book cover.",
    )
    isbn: str = Field(description="ISBN identifier for the book.")
