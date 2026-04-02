from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field

from .authors import add_authors
from .book_authors import add_book_authors
from .book_categories import add_book_categories
from .books import add_books
from .categories import add_category
from .connection import _get_db
from .models import Author, Book, Category


# ---------------------------------------------------------
# Pydantic Models (Schemas)
# ---------------------------------------------------------
class AddFullBooks(BaseModel):
    book: Book = Field(..., description="Book to add to the Database")
    authors: list[Author] = Field(
        ..., description="Name of the book's authors", min_length=1
    )
    categories: list[Category] | None = Field(default=None, description="Categories of the book")

class BulkInsertResponse(BaseModel):
    status: str
    message: str
    processed_count: int


# ---------------------------------------------------------
# Business Logic
# ---------------------------------------------------------
def _add_single_book(book_data: AddFullBooks, conn):
    """
    Handles the insertion of a single book and its relationships.
    Raises ValueError if any step fails, which triggers a rollback in the parent function.
    """
    # 1. Add the book
    book_response = add_books(books_to_add=[book_data.book], conn=conn)[0]

    # 2. Add the authors
    authors_response = add_authors(authors_to_add=book_data.authors, conn=conn)

    # 3. Create Book-Author associations
    author_links = [(book_response.id_, auth.id_) for auth in authors_response]
    if add_book_authors(associations=author_links, conn=conn).get("status") != "ok":
        raise ValueError("Failed to link authors to the book.")

    # 4. Handle Categories (if provided)
    if book_data.categories:
        cat_links = []
        for cat in book_data.categories:
            cat_res = add_category(category_name=cat.name, conn=conn)
            if cat_res.status != "ok":
                raise ValueError(f"Failed to add category: {cat.name}")
            cat_links.append((book_response.id_, cat_res.id_))

        add_book_categories(associations=cat_links, conn=conn)


# ---------------------------------------------------------
# Endpoint Controller Function
# ---------------------------------------------------------
def add_book_full(
    payload: list[AddFullBooks], conn=Depends(_get_db)
) -> BulkInsertResponse:
    """
    Processes a list of books to add to the database.
    Uses transaction rollback to prevent partial inserts if an error occurs.
    """  # noqa: D205, D401
    processed_count = 0

    try:
        for book_data in payload:
            _add_single_book(book_data=book_data, conn=conn)
            processed_count += 1

        # Commit the transaction only if the entire loop succeeds
        conn.commit()

    except Exception as e:
        # Rollback all changes made in this session to prevent corrupted data states
        conn.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction failed at book index {processed_count}. Error: {str(e)}. All changes rolled back.",
        ) from e

    return BulkInsertResponse(
        status="success",
        message="All books successfully added.",
        processed_count=processed_count,
    )