from typing import Literal

from fastapi import FastAPI

from src.book_api.google_books import (
    GoogleBookRetriever,
    GoogleBookSlimResponse,
    GoogleBooksResponse,
)

app = FastAPI()

books_retriever = GoogleBookRetriever()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Book Library API! Use /search_book/{isbn}/{mode} to search for books."
    }


@app.get("/search_book/{isbn}/{mode}")
def search_book(isbn: str, mode: Literal["slim", "full"]) -> GoogleBooksResponse | GoogleBookSlimResponse:
    """Search for a book by its ISBN."""
    try:
        match mode:
            case "slim":
                book_info = books_retriever.get_flatten_response(isbn)
            case "full":
                book_info = books_retriever.get_book_info(isbn)
            case _:
                raise ValueError(f"Mode {mode} not supported, choose one between 'slim' and 'full'.")
        return book_info
    except Exception as e:
        return {"error": str(e)}
