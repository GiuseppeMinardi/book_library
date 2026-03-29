"""
Module for interacting with the Google Books API.

This module provides the `GoogleBookRetriever` class, which allows users to:
- Construct requests to the Google Books API.
- Fetch and parse book information by ISBN.
- Retrieve flattened metadata for books.

Dependencies:
- `requests`: For making HTTP requests to the Google Books API.
- `GoogleBooksResponse` and `GoogleBooksSettings`: Models for handling API responses and settings.
"""

import requests

from .google_books_models import (
    GoogleBookSlimResponse,
    GoogleBooksResponse,
    GoogleBooksSettings,
)

gsettings = GoogleBooksSettings()


class GoogleBookRetriever:
    """Retrieve book data from the Google Books API.

    Purpose
    -------
    Provide helpers to construct requests to the Google Books API and to
    fetch/parse book information by ISBN.

    Attributes
    ----------
    api_key : SecretStr | str
        API key used to authenticate requests (sourced from GoogleBooksSettings).
    base_url : str
        Base endpoint URL for the Google Books API.

    Methods
    -------
    get_book_url(isbn: str) -> str
        Build the request URL for the given ISBN.
    get_book_info(isbn: str) -> GoogleBooksResponse
        Fetch and validate a GoogleBooksResponse model for the ISBN.
    get_flatten_response(isbn: str) -> dict
        Return a flattened dictionary of key metadata for the book.
    """

    def __init__(self, settings: GoogleBooksSettings = gsettings):
        self.api_key = settings.api_key
        self.base_url = settings.base_url

    def __repr__(self) -> str:
        """Provide a string representation of the GoogleBookRetriever instance.

        Returns
        -------
        str
            A string showing the base URL and a masked API key.
        """
        return f"GoogleBookretriever(base_url={self.base_url}, api_key={self.api_key.get_secret_value()[:4]}****)"

    def __str__(self) -> str:
        """Provide a user-friendly string representation of the instance.

        Returns
        -------
        str
            A string describing the Google Books API base URL being used.
        """
        return f"GoogleBookretriever using Google Books API at {self.base_url}"

    def get_book_url(self, isbn: str) -> str:
        """Build the request URL for the given ISBN.

        Parameters
        ----------
        isbn : str
            The ISBN of the book to look up.

        Returns
        -------
        str
            The complete URL for querying the Google Books API with the given ISBN.
        """
        return f"{self.base_url}?q=isbn:{isbn}&key={self.api_key.get_secret_value()}"

    def get_book_info(self, isbn: str) -> GoogleBooksResponse:
        """Retrieve book information from Google Books API by ISBN.

        Parameters
        ----------
        isbn : str
            The ISBN of the book to look up.

        Returns
        -------
        GoogleBooksResponse
            A validated GoogleBooksResponse model built from the API item.

        Raises
        ------
        ValueError
            If the API returns a non-200 HTTP status code.
        IndexError
            If the API response contains no 'items' for the provided ISBN.
        requests.RequestException
            If a network-related error occurs while making the HTTP request.
        """
        url: str = self.get_book_url(isbn)

        response: requests.Response = requests.get(url)

        if response.status_code == 200:
            dict_response = response.json()
            if "items" not in dict_response or len(dict_response["items"]) == 0:
                raise IndexError(f"No items found for ISBN: {isbn}")
            response_json: dict = response.json().get("items", [])[0]
            return GoogleBooksResponse.model_validate(response_json)
        else:
            raise ValueError(f"Error fetching data: {response.status_code}")
    
    @staticmethod
    def flatten_response(
        full_response: GoogleBooksResponse, isbn: str
    ) -> GoogleBookSlimResponse:
        """Flatten a GoogleBooksResponse to a GoogleBookSlimResponse.

        Parameters
        ----------
        full_response : GoogleBooksResponse
            The full API response model to flatten.
        isbn : str
            The ISBN of the book.

        Returns
        -------
        GoogleBookSlimResponse
            A validated slim response model with essential book metadata.
        """
        slim_response = {
            "kind": full_response.kind,
            "title": full_response.volume_info.title,
            "authors": full_response.volume_info.authors,
            "publisher": full_response.volume_info.publisher,
            "publishedDate": full_response.volume_info.published_date,
            "description": full_response.volume_info.description,
            "pageCount": full_response.volume_info.page_count,
            "categories": full_response.volume_info.categories,
            "printType": full_response.volume_info.print_type,
            "language": full_response.volume_info.language,
            "infoLink": full_response.volume_info.info_link,
            "smallThumbnail": (
                full_response.volume_info.image_links.small_thumbnail
                if full_response.volume_info.image_links
                else None
            ),
            "isbn": isbn,
        }

        return GoogleBookSlimResponse.model_validate(slim_response)

    def get_flatten_response(self, isbn: str) -> GoogleBookSlimResponse:
        """Retrieve and flatten book information from Google Books API by ISBN.

        Parameters
        ----------
        isbn : str
            The ISBN of the book to look up.

        Returns
        -------
        dict
            A flattened dictionary representation of the GoogleBooksResponse model.

        Raises
        ------
        ValueError
            If the API returns a non-200 HTTP status code.
        IndexError
            If the API response contains no 'items' for the provided ISBN.
        requests.RequestException
            If a network-related error occurs while making the HTTP request.
        """
        book_info: dict = self.get_book_info(isbn)
        return self.flatten_response(book_info, isbn=isbn)
