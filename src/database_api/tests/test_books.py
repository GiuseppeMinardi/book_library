"""Tests for the books module."""

import pytest

from src.books import get_books, add_book, update_book, book_exists, add_book_embedding
from src.models import Book, BookEmbedding


def test_get_books_no_filter(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (
            "1",
            "Book1",
            "Publisher",
            "2023",
            "Desc",
            100,
            "BOOK",
            "en",
            "http://link",
            "thumb",
            "1234567890",
        )
    ]

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = get_books()
    assert "1" in result
    assert result["1"].title == "Book1"
    mock_cursor.execute.assert_called_once()


def test_get_books_with_filter(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (
            "1",
            "Book1",
            "Publisher",
            "2023",
            "Desc",
            100,
            "BOOK",
            "en",
            "http://link",
            "thumb",
            "1234567890",
        )
    ]


    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = get_books(books_id=["1"])

    assert "1" in result
    mock_cursor.execute.assert_called()


def test_add_book_new(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [None, "1"]  # No existing, returned ID

    book = Book(id="0", title="New Book")

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = add_book(book)

    assert result["id"] == "1"
    assert result["message"] == "Book created successfully"
    mock_conn.commit.assert_called_once()


def test_add_book_existing(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Existing book

    book = Book(id="0", title="Existing Book")

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = add_book(book)

    assert result["id"] == "1"
    assert result["message"] == "Book already exists"
    mock_conn.commit.assert_not_called()


def test_update_book_exists(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Book exists

    book = Book(id="0", title="Updated Book")

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = update_book("1", book)

    mock_conn.commit.assert_called_once()


def test_update_book_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Book not found

    book = Book(id="0", title="Updated Book")

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = update_book("1", book)

    assert result["message"] == "Book not found"
    mock_conn.commit.assert_not_called()


def test_book_exists_true(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = book_exists("1")

    assert result is True


def test_book_exists_false(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = book_exists("1")

    assert result is False


def test_add_book_embedding_success(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Book exists

    embedding = BookEmbedding(
        book_id="1",
        model_name="test",
        vector=[0.1, 0.2],
        created_at="2023-01-01T00:00:00",
    )

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = add_book_embedding(embedding)

    assert result["message"] == "Embedding added successfully"
    mock_conn.commit.assert_called_once()


def test_add_book_embedding_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Book not found

    embedding = BookEmbedding(
        book_id="1",
        model_name="test",
        vector=[0.1, 0.2],
        created_at="2023-01-01T00:00:00",
    )

    mocker.patch("src.books.get_connection", return_value=mock_conn)
    result = add_book_embedding(embedding)

    assert result["message"] == "Book not found"
    mock_conn.commit.assert_not_called()
