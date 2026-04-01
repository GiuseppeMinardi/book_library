import numpy as np
from pathlib import Path
import pytest
import json
from src.book_authors import get_book_authors, add_book_authors

def test_book_authors(db_session):
    res = get_book_authors(book_id=1, conn=db_session)

    assert isinstance(res, list)
    assert len(res) == 1

def test_add_book_authors(db_session):
    from src.books import add_books, Book
    from src.authors import add_authors, Author

    book = Book(
        id=0,
        title="A Book",
        isbn="934875678467"
    )
    author = Author(
        id=0,
        name="Pippo Franco"
    )

    authors_added = add_authors(authors_to_add=[author], conn=db_session)
    books_added = add_books(books_to_add=[book], conn=db_session)

    connections_to_add = [
        (book_added.id_, author_added.id_)
        for author_added, book_added in zip(authors_added, books_added)
    ]

    res = add_book_authors(associations=connections_to_add, conn=db_session)

    assert res.get("status") == "ok"