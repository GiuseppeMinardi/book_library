
from fastapi import Depends, Query
from pydantic import BaseModel, Field

from .authors import add_authors
from .book_authors import add_book_authors
from .book_categories import add_book_categories
from .books import add_books
from .categories import add_category
from .connection import _get_db
from .models import Author, Book, Category


class AddFullBooks(BaseModel):
    book: Book = Field(default=..., description="Book to add to the Database")
    authors: list[Author] = Field(default=..., description="Name of the book's authors", min_length=1)
    categories: list[Category] | None = Field(default=None, description="Categories of the book")

def _add_single_book(book:AddFullBooks, conn):
    book_response = add_books(books_to_add=[book.book], conn=conn)[0]
    authors_response = add_authors(authors_to_add=book.authors, conn=conn)
    
    book_authors_associations = [
        (book_response.id_, author_response.id_)
        for author_response in authors_response
    ]

    res = add_book_authors(associations=book_authors_associations, conn=conn)

    if res.get("status") != "ok":
        raise ValueError("Something went wrong")

    cats = book.categories
    cats_associations = []
    if cats is not None and isinstance(cats, list):
        for cat in cats:
            category_response = add_category(category_name=cat.name, conn=conn)
            if category_response.status != "ok":
                raise ValueError("Something went wrong")
            cats_associations.append((book_response.id_, category_response.id_))
        add_book_categories(associations=cats_associations, conn=conn)
        


def add_book_full(
    payload: list[AddFullBooks] = Query(default=..., min_length=1),
    conn=Depends(_get_db())
):
    for book in payload:
        try:
            _add_single_book(book=book, conn=conn)
            return {"status": "ok", "message": "Book added in full"}
        except Exception as e:
            return {"status": "error", "message": e}