"""Tests for the categories module."""

import pytest

from src.categories import (
    get_categories,
    add_category,
    update_category,
    category_exists,
)
from src.models import Category


def test_get_categories_no_filter(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("1", "Fiction")]

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = get_categories()

    assert "1" in result
    assert result["1"].name == "Fiction"
    mock_cursor.execute.assert_called_once()


def test_get_categories_with_filter(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("1", "Fiction")]

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = get_categories(categories_id=["1"])

    assert "1" in result
    mock_cursor.execute.assert_called()


def test_add_category_new(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [None, "1"]  # No existing, returned ID

    category = Category(id="0", name="New Category")

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = add_category(category)

    assert result["id"] == "1"
    assert result["message"] == "Category created successfully"
    mock_conn.commit.assert_called_once()


def test_add_category_existing(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Existing category

    category = Category(id="0", name="Existing Category")

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = add_category(category)

    assert result["id"] == "1"
    assert result["message"] == "Category already exists"
    mock_conn.commit.assert_not_called()


def test_update_category_exists(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"  # Category exists

    category = Category(id="0", name="Updated Category")

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = update_category("1", category)

    mock_conn.commit.assert_called_once()


def test_update_category_not_found(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Category not found

    category = Category(id="0", name="Updated Category")

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = update_category("1", category)

    assert result["message"] == "Category not found"
    mock_conn.commit.assert_not_called()


def test_category_exists_true(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = "1"

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = category_exists("1")

    assert result is True


def test_category_exists_false(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    mocker.patch("src.categories.get_connection", return_value=mock_conn)
    result = category_exists("1")

    assert result is False
