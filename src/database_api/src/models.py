"""Database models for the book library API.

This module defines Pydantic models for database entities including books, authors,
categories, and their relationships, with support for camelCase serialization.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, HttpUrl
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model configured to support alias-based serialization (camelCase)."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


# --- Core tables ---


class Book(CamelModel):
    """Represents a book entity with metadata such as title, publisher, and identifiers."""

    id: int = Field(description="Unique identifier for the book")
    title: str = Field(description="Title of the book")
    publisher: str | None = Field(default=None, description="Publisher of the book")
    published_date: str | None = Field(
        default=None,
        description="Publication date (kept as string due to varying formats)",
    )
    description: str | None = Field(
        default=None, description="Book description or summary"
    )
    page_count: int | None = Field(default=None, description="Number of pages")
    print_type: str | None = Field(
        default=None, description="Print type (e.g., BOOK, MAGAZINE)"
    )
    language: str | None = Field(default=None, description="Language of the book")
    info_link: HttpUrl | None = Field(
        default=None, description="External information link"
    )
    small_thumbnail: HttpUrl | None = Field(
        default=None,
        description="URL to a small thumbnail image",
    )
    isbn: str | None = Field(
        default=None,
        description="International Standard Book Number (unique identifier)",
    )


class Author(CamelModel):
    """Represents an author with personal details and optional biography."""

    id: int | None = Field(default=None, description="Unique identifier for the author")
    name: str = Field(description="Full name of the author")
    birth_date: Optional[date] = Field(default=None, description="Author's birth date")
    death_date: Optional[date] = Field(default=None, description="Author's death date")
    nationality: Optional[str] = Field(default=None, description="Author's nationality")
    sex: Optional[str] = Field(default=None, description="Author's sex")
    bio: Optional[str] = Field(
        default=None, description="Short biography of the author"
    )
    author_link: Optional[AnyUrl] = Field(
        default=None,
        alias="authorLink",
        description="External link with more information about the author",
    )


class Category(CamelModel):
    """Represents a classification or genre assigned to books."""

    id: int | None = Field(
        default=None, description="Unique identifier for the category"
    )
    name: str = Field(description="Category name")


# --- Association tables (composite PKs) ---


class BookAuthor(CamelModel):
    """Associative entity linking books and authors (many-to-many relationship)."""

    book_id: str = Field(alias="bookId", description="Reference to the book ID")
    author_id: str = Field(alias="authorId", description="Reference to the author ID")


class BookCategory(CamelModel):
    """Associative entity linking books and categories (many-to-many relationship)."""

    book_id: str = Field(alias="bookId", description="Reference to the book ID")
    category_id: str = Field(
        alias="categoryId", description="Reference to the category ID"
    )


# --- Embeddings tables (composite PKs) ---


class BookEmbedding(CamelModel):
    """Stores vector embeddings associated with a book for a specific model."""

    book_id: int = Field(
        default=0, alias="bookId", description="Reference to the book ID"
    )
    model_name: str = Field(
        alias="modelName", description="Name of the embedding model"
    )
    vector: List[float] = Field(
        description="Embedding vector as a list of numerical values"
    )
    created_at: datetime = Field(
        alias="createdAt", description="Timestamp when the embedding was created"
    )


class AuthorEmbedding(CamelModel):
    """Stores vector embeddings associated with an author for a specific model."""

    author_id: int = Field(
        default=0, alias="authorId", description="Reference to the author ID"
    )
    model_name: str = Field(
        alias="modelName", description="Name of the embedding model"
    )
    vector: List[float] = Field(
        description="Embedding vector as a list of numerical values"
    )
    created_at: datetime = Field(
        alias="createdAt", description="Timestamp when the embedding was created"
    )
