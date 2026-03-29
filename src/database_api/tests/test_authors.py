"""Tests for the authors module."""

import pytest

from src.authors import (
    get_authors,
    add_author,
    update_author,
    author_exists,
    add_author_embedding,
)
from src.models import Author, AuthorEmbedding


def test_get_authors_no_filter(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        ("1", "Author1", "1990-01-01", None, "US", "M", "Bio", "http://link")
    ]

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = get_authors()

    assert "1" in result
    assert result["1"].name == "Author1"
    mock_cursor.execute.assert_called_once()


def test_get_authors_with_filter(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        ("1", "Author1", "1990-01-01", None, "US", "M", "Bio", "http://link")
    ]

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = get_authors(authors_id=["1"])

    assert "1" in result
    mock_cursor.execute.assert_called()


def test_add_author_new(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [None, "1"]  # No existing, returned ID

    author = Author(name="New Author")

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = add_author(author)

    assert result["id"] == "1"
    assert result["message"] == "Author created successfully"
    mock_conn.commit.assert_called_once()


def test_add_author_existing(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Existing author

    author = Author(name="Existing Author")

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = add_author(author)

    assert result["id"] == "1"
    assert result["message"] == "Author already exists"
    mock_conn.commit.assert_not_called()


def test_update_author_exists(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Author exists

    author = Author(name="Updated Author")

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = update_author("1", author)

    mock_conn.commit.assert_called_once()


def test_update_author_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Author not found

    author = Author(name="Updated Author")

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = update_author("1", author)

    assert result["message"] == "Author not found"
    mock_conn.commit.assert_not_called()


def test_author_exists_true(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = author_exists("1")

    assert result is True


def test_author_exists_false(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = author_exists("1")

    assert result is False


def test_add_author_embedding_success(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Author exists

    embedding = AuthorEmbedding(
        author_id="1",
        model_name="test",
        vector=[0.1, 0.2],
        created_at="2023-01-01T00:00:00",
    )

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = add_author_embedding(embedding)

    assert result["message"] == "Embedding added successfully"
    mock_conn.commit.assert_called_once()


def test_add_author_embedding_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Author not found

    embedding = AuthorEmbedding(
        author_id="1",
        model_name="test",
        vector=[0.1, 0.2],
        created_at="2023-01-01T00:00:00",
    )

    mocker.patch("src.authors.get_connection", return_value=mock_conn)
    result = add_author_embedding(embedding)

    assert result["message"] == "Author not found"
    mock_conn.commit.assert_not_called()
