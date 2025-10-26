import json
from pathlib import Path
from typing import Annotated

from .agent.agent import book_summary_agent
from .book_api import GoogleBookRetriever
from .database.db import Database
from .logger import logger
from .models.google_books import GoogleBookSlimResponse, GoogleBooksResponse

ISBN = Annotated[str, "International Standard Book Number"]

db = Database()

data_folder = Path(__file__).parents[1].joinpath("data", "isbn_response")
data_folder.mkdir(parents=True, exist_ok=True)

retriever = GoogleBookRetriever()



def add_book_from_isbn(isbn: ISBN) -> None:
    """
    Add a book to the database using its ISBN.

    This function retrieves book information from an external API using the provided ISBN.
    If the book is not already in the database, it processes the data, generates a summary
    if necessary, and stores the book information in the database and a local JSON file.

    Parameters
    ----------
    isbn : ISBN
        The International Standard Book Number of the book to be added.

    Returns
    -------
    None
    """
    query = f"Select isbn from books where isbn = {isbn!r}"
    with db:
        res: list[dict] = db.run_query(query, as_dataframe=False)
        if res is not None and isinstance(res, list) and len(res) > 0:
            logger.info(f"ISBN {isbn} already in database. Skipping.")
            return

        try:
            book_data = retriever.get_book_info(isbn)
            book_title: str = book_data.volumeInfo.title
            book_authors: str = ", ".join(book_data.volumeInfo.authors)
            logger.info(f"Processing book: {book_title} by  {book_authors}.")
            flat_book_data = retriever.flatten_response(book_data, isbn=isbn)
            if (
                not flat_book_data.description
                or flat_book_data.description.strip() == ""
            ):
                logger.warning(f"Generating summary for book: {book_title}")
                summary_response = book_summary_agent.run_sync(
                    f"{book_title} by {book_authors}"
                ).output
                if len(summary_response) == 0 or summary_response is None:
                    logger.warning(
                        f"Summary generation returned empty for book: {book_title}"
                    )
                flat_book_data.description = summary_response
            db.add_book(flat_book_data)
            logger.info(f"Added book {book_title} to database.")
            with data_folder.joinpath(f"{isbn}.json").open("w", encoding="utf-8") as f:
                json.dump(book_data.model_dump(), f, ensure_ascii=False, indent=4)
        except (ValueError, IndexError) as e:
            logger.error(f"Error retrieving data for ISBN {isbn}: {e}")
            return


def add_books_from_isbn_list(isbn_list: list[ISBN]) -> None:
    """
    Add multiple books to the database using a list of ISBNs.

    This function iterates over a list of ISBNs, retrieves book information
    from an external API for each ISBN, and adds the book to the database
    if it is not already present. It also generates summaries for books
    without descriptions and saves the book data to local JSON files.

    Parameters
    ----------
    isbn_list : list[ISBN]
        A list of International Standard Book Numbers to be added.

    Returns
    -------
    None
    """
    with db:
        res: list[dict] = db.run_query("Select isbn from books", as_dataframe=False)
        if res is not None and isinstance(res, list):
            isbn_in_df = [row.get("isbn") for row in res]

        for isbn in isbn_list:
            if isbn in isbn_in_df:
                logger.info(f"ISBN {isbn} already in database. Skipping.")
                continue
            try:
                book_data: GoogleBooksResponse = retriever.get_book_info(isbn)
                book_title: str = book_data.volumeInfo.title
                book_authors: str = ", ".join(book_data.volumeInfo.authors)
                logger.info(f"Processing book: {book_title} by  {book_authors}.")
                flat_book_data: GoogleBookSlimResponse = retriever.flatten_response(
                    book_data, isbn=isbn
                )
                if (
                    not flat_book_data.description
                    or flat_book_data.description.strip() == ""
                ):
                    logger.warning(f"Generating summary for book: {book_title}")
                    summary_response = book_summary_agent.run_sync(
                        f"{book_title} by {book_authors}"
                    ).output
                    if len(summary_response) == 0 or summary_response is None:
                        logger.warning(
                            f"Summary generation returned empty for book: {book_title}"
                        )
                    flat_book_data.description = summary_response
                db.add_book(flat_book_data)
                logger.info(f"Added book {book_title} to database.")
                with data_folder.joinpath(f"{isbn}.json").open(
                    "w", encoding="utf-8"
                ) as f:
                    json.dump(book_data.model_dump(), f, ensure_ascii=False, indent=4)
            except (ValueError, IndexError) as e:
                logger.error(f"Error retrieving data for ISBN {isbn}: {e}")
                continue
