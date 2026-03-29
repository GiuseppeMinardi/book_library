"""Tests for the associations module."""

import pytest

from src.associations import (
    get_book_authors,
    get_book_categories,
    add_book_author,
    add_book_category,
)


def test_get_book_authors(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("1",), ("2",)]

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = get_book_authors("book1")

    assert result == ["1", "2"]
    mock_cursor.execute.assert_called_once_with(
        "SELECT author_id FROM book_authors WHERE book_id = %s;", ("book1",)
    )


def test_get_book_categories(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("1",), ("2",)]

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = get_book_categories("book1")

    assert result == ["1", "2"]
    mock_cursor.execute.assert_called_once_with(
        "SELECT category_id FROM book_categories WHERE book_id = %s;", ("book1",)
    )


def test_add_book_author_success(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    # Book exists, author exists, no association
    mock_cursor.fetchone.side_effect = ["1", "1", None]

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_author("book1", "author1")

    assert result["message"] == "Association added successfully"
    mock_conn.commit.assert_called_once()


def test_add_book_author_book_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Book not found

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_author("book1", "author1")

    assert result["message"] == "Book not found"
    mock_conn.commit.assert_not_called()


def test_add_book_author_author_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = ["1", None]  # Book exists, author not

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_author("book1", "author1")

    assert result["message"] == "Author not found"
    mock_conn.commit.assert_not_called()


def test_add_book_author_already_exists(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = ["1", "1", "1"]  # All exist, association exists

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_author("book1", "author1")

    assert result["message"] == "Association already exists"
    mock_conn.commit.assert_not_called()


def test_add_book_category_success(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    # Book exists, category exists, no association
    mock_cursor.fetchone.side_effect = ["1", "1", None]

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_category("book1", "cat1")

    assert result["message"] == "Association added successfully"
    mock_conn.commit.assert_called_once()


def test_add_book_category_book_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Book not found

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_category("book1", "cat1")

    assert result["message"] == "Book not found"
    mock_conn.commit.assert_not_called()


def test_add_book_category_category_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = ["1", None]  # Book exists, category not

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_category("book1", "cat1")

    assert result["message"] == "Category not found"
    mock_conn.commit.assert_not_called()


def test_add_book_category_already_exists(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = ["1", "1", "1"]  # All exist, association exists

    mocker.patch("src.associations.get_connection", return_value=mock_conn)
    result = add_book_category("book1", "cat1")

    assert result["message"] == "Association already exists"
    mock_conn.commit.assert_not_called()
