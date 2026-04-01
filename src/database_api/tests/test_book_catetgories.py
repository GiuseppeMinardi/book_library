import numpy as np
from pathlib import Path
import pytest
import json
from src.book_categories import get_book_categories, add_book_categories

def test_book_categories(db_session):
    res = get_book_categories(book_id=1, conn=db_session)

    assert isinstance(res, list)
    assert len(res) == 2

def test_add_book_authors(db_session):
    from src.books import add_books, Book
    from src.categories import add_category

    book = Book(
        id=0,
        title="A Book",
        isbn="934875678467"
    )
    categories = ["Fantasy", "Circus"]

    book_added = add_books(books_to_add=[book], conn=db_session)[0]
    categories_ids = []
    for category in categories:
        category_added = add_category(category_name=category, conn=db_session)
        assert category_added.status == "ok"
        categories_ids.append(category_added)

    connections_to_add = [
        (book_added.id_, categories_ids[0].id_),
        (book_added.id_, categories_ids[1].id_),
    ]

    res = add_book_categories(associations=connections_to_add, conn=db_session)

    assert res.get("status") == "ok"