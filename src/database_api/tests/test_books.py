from pathlib import Path
import pytest
import json
from src import books
from src.models import Book
from src.books import add_books, delete_books, get_books, update_books, delete_books

def test_add_books(db_session):
    exaples_books_path = Path(__file__).parent.joinpath("examples", "books.json")
    with exaples_books_path.open() as f:
        books_data = [Book(**book) for book in json.load(f)]

    res = add_books(books_to_add=books_data, conn=db_session)
    assert len(res) == len(books_data)
    for book_res in res:
        assert book_res.status == "ok"
        assert book_res.exists == False

def test_get_books(db_session):
    examople_books = [
        Book(
            id=1,
            title="The Hobbit",
            publisher="George Allen & Unwin",
            published_date="1937-09-21",
            isbn="9780007525492",
        ),
        Book(
            id=2,
            title="A Brief History of Time",
            publisher="Bantam Books",
            published_date="1988-04-01",
            isbn="9780553380163",
        ),
    ]
    # test get books by isbs
    isbns = [book.isbn for book in examople_books]
    books_res = get_books(books_isbn=isbns, conn=db_session)
    assert len(books_res) == len(examople_books)
    for book_isbn, book in books_res.items():
        assert book.isbn in isbns

    # test gest_books by title
    titles = [book.title for book in examople_books]
    books_res = get_books(books_titles=titles, conn=db_session)
    assert len(books_res) == len(examople_books)
    for book_title, book in books_res.items():
        assert book.title in titles

    # test title and isbn together
    books_res = get_books(
        books_isbn=[examople_books[0].isbn],
        books_titles=[examople_books[1].title],
        conn=db_session,
    )
    assert len(books_res) == 2

    # test problems when nothing is passed
    with pytest.raises(ValueError):
        books_res = get_books(conn=db_session)

def test_update_books(db_session):
    # add a book to update
    book_to_add = Book(
        id=1,
        title="The Hobbit",
        publisher="George Allen & Unwin",
        published_date="1937-09-21",
        isbn="9780007525492",
    )
    add_books(books_to_add=[book_to_add], conn=db_session)

    # update the book
    updated_book = Book(
        id=1,
        title="The Hobbit: An Unexpected Journey",
        publisher="George Allen & Unwin",
        published_date="1937-09-21",
        isbn="9780007525492",
    )
    res = update_books(books_to_update=[updated_book], conn=db_session)
    assert len(res) == 1
    assert res[0].status == "ok"
    assert res[0].exists == True

def test_delete_books(db_session):
    # add a book to delete
    book_to_add = Book(
        id=1,
        title="The Hobbit",
        publisher="George Allen & Unwin",
        published_date="1937-09-21",
        isbn="9780007525492",
    )
    add_books(books_to_add=[book_to_add], conn=db_session)

    # delete the book
    res = delete_books(books_ids=[str(book_to_add.id)], conn=db_session)
    assert res[0].status == "ok"

    # try to get the deleted book
    books_res = get_books(books_isbn=[book_to_add.isbn], conn=db_session)
    assert len(books_res) == 0

    # test delete on a book that does not exists
    res = delete_books(books_ids=[str(99999)], conn=db_session)
    assert res[0].status == "error"