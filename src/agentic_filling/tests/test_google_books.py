import importlib
import sys
from types import SimpleNamespace
from pydantic import SecretStr
import pytest


def import_google_books_with_env(monkeypatch):
    """Import the google_books module after ensuring the API key env var.

    We remove any cached modules so the module-level `GoogleBooksSettings`
    initialization picks up the environment variable set by the test.
    """
    monkeypatch.setenv("GOOGLE_BOOKS_API_KEY", "DUMMY_KEY")
    for mod in ("src.book_api.google_books", "src.book_api.google_books_models"):
        if mod in sys.modules:
            del sys.modules[mod]
    return importlib.import_module("src.book_api.google_books")


class MockResponse:
    def __init__(self, json_data, status_code):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


class DummySettings:
    def __init__(self, api_key_str, base_url):
        self.api_key = SecretStr(api_key_str)
        self.base_url = base_url


def test_get_book_url(monkeypatch):
    mod = import_google_books_with_env(monkeypatch)
    settings = DummySettings("APIKEY123", "https://example.com")
    retriever = mod.GoogleBookRetriever(settings)

    assert retriever.get_book_url("978") == "https://example.com?q=isbn:978&key=APIKEY123"


def test_flatten_response(monkeypatch):
    mod = import_google_books_with_env(monkeypatch)
    # Build a realistic API item and validate it into the pydantic model
    full_item = {
        "kind": "books#volume",
        "id": "abc",
        "etag": "etag",
        "selfLink": "http://self",
        "volumeInfo": {
            "title": "MyTitle",
            "authors": ["Author One"],
            "publisher": "Pub",
            "publishedDate": "2020-01-01",
            "description": "Desc",
            "pageCount": 250,
            "categories": ["Fiction"],
            "printType": "BOOK",
            "language": "en",
            "infoLink": "http://info",
            "imageLinks": {"smallThumbnail": "http://thumb"},
        },
    }

    full = mod.GoogleBooksResponse.model_validate(full_item)

    slim = mod.GoogleBookRetriever.flatten_response(full, isbn="978-1")
    dump = slim.model_dump(by_alias=True)

    # Ensure flattened fields match the corresponding fields from the full response
    v = full.volume_info
    assert dump["title"] == v.title
    assert dump["authors"] == v.authors
    assert dump["publisher"] == v.publisher
    assert dump["publishedDate"] == v.published_date
    assert dump["description"] == v.description
    assert dump["pageCount"] == v.page_count
    assert dump["categories"] == v.categories
    assert dump["printType"] == v.print_type
    assert dump["language"] == v.language
    assert dump["infoLink"] == v.info_link
    assert dump["smallThumbnail"] == v.image_links.small_thumbnail
    assert dump["isbn"] == "978-1"


def test_get_book_info_success(monkeypatch):
    mod = import_google_books_with_env(monkeypatch)

    sample_item = {
        "kind": "books#volume",
        "id": "abc",
        "etag": "etag",
        "selfLink": "http://self",
        "volumeInfo": {
            "title": "MyTitle",
            "authors": ["Author One"],
            "publisher": "Pub",
            "publishedDate": "2020-01-01",
            "description": "Desc",
            "pageCount": 250,
            "categories": ["Fiction"],
            "printType": "BOOK",
            "language": "en",
            "infoLink": "http://info",
            "imageLinks": {"smallThumbnail": "http://thumb"},
        },
    }

    mock = MockResponse({"items": [sample_item]}, 200)
    monkeypatch.setattr(mod.requests, "get", lambda url: mock)

    retriever = mod.GoogleBookRetriever(DummySettings("KEY", "https://example.com"))
    resp = retriever.get_book_info("978")
    dump = resp.model_dump(by_alias=True)

    assert dump["kind"] == "books#volume"
    assert dump["volumeInfo"]["title"] == "MyTitle"


def test_get_book_info_no_items_raises(monkeypatch):
    mod = import_google_books_with_env(monkeypatch)
    mock = MockResponse({"items": []}, 200)
    monkeypatch.setattr(mod.requests, "get", lambda url: mock)

    retriever = mod.GoogleBookRetriever(DummySettings("KEY", "https://example.com"))
    with pytest.raises(IndexError):
        retriever.get_book_info("978")


def test_get_book_info_non_200_raises(monkeypatch):
    mod = import_google_books_with_env(monkeypatch)
    mock = MockResponse({}, 404)
    monkeypatch.setattr(mod.requests, "get", lambda url: mock)

    retriever = mod.GoogleBookRetriever(DummySettings("KEY", "https://example.com"))
    with pytest.raises(ValueError):
        retriever.get_book_info("978")


def test_get_flatten_response_end_to_end(monkeypatch):
    mod = import_google_books_with_env(monkeypatch)

    sample_item = {
        "kind": "books#volume",
        "id": "abc",
        "etag": "etag",
        "selfLink": "http://self",
        "volumeInfo": {
            "title": "MyTitle",
            "authors": ["Author One"],
            "publisher": "Pub",
            "publishedDate": "2020-01-01",
            "description": "Desc",
            "pageCount": 250,
            "categories": ["Fiction"],
            "printType": "BOOK",
            "language": "en",
            "infoLink": "http://info",
            "imageLinks": {"smallThumbnail": "http://thumb"},
        },
    }

    mock = MockResponse({"items": [sample_item]}, 200)
    monkeypatch.setattr(mod.requests, "get", lambda url: mock)

    retriever = mod.GoogleBookRetriever(DummySettings("KEY", "https://example.com"))
    slim = retriever.get_flatten_response("978-1")
    dump = slim.model_dump(by_alias=True)

    assert dump["title"] == "MyTitle"
    assert dump["smallThumbnail"] == "http://thumb"
    assert dump["isbn"] == "978-1"
