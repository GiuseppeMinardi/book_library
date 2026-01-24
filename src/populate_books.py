import json
from pathlib import Path
from typing import Annotated

from .agent.agent import book_summary_agent
from .book_api import GoogleBookRetriever
from .database.db import Database
from .logger import logger

ISBN = Annotated[str, "International Standard Book Number"]

db = Database()

data_folder = Path(__file__).parents[1].joinpath("data", "isbn_response")
data_folder.mkdir(parents=True, exist_ok=True)

retriever = GoogleBookRetriever()



def add_book_from_isbn(isbn: ISBN) -> None:
    """Add a single book to the database using its ISBN."""
    # FIX 1: Use parameterized query for security
    query = "SELECT isbn FROM books WHERE isbn = ?"

    with db:
        # Pass the ISBN as a tuple in 'params'
        res: list[dict] = db.run_query(query, params=(str(isbn),), as_dataframe=False)

        if res and len(res) > 0:
            logger.info(f"ISBN {isbn} already in database. Skipping.")
            return

        try:
            book_data = retriever.get_book_info(isbn)
            # Safe navigation in case volumeInfo is missing
            book_title = book_data.volumeInfo.title
            authors_list = book_data.volumeInfo.authors or []
            book_authors = ", ".join(authors_list)

            logger.info(f"Processing book: {book_title} by {book_authors}.")

            flat_book_data = retriever.flatten_response(book_data, isbn=isbn)

            # Check for missing description
            if not flat_book_data.description or not flat_book_data.description.strip():
                logger.warning(f"Generating summary for book: {book_title}")

                summary_response = book_summary_agent.run_sync(
                    f"{book_title} by {book_authors}"
                ).output

                # FIX 2: Check None BEFORE checking len()
                if summary_response is None or len(summary_response) == 0:
                    logger.warning(
                        f"Summary generation returned empty for book: {book_title}"
                    )
                else:
                    flat_book_data.description = summary_response

            # Database Class handles author duplication logic internally now
            db.add_book(flat_book_data)

            logger.info(f"Added book {book_title} to database.")

            with data_folder.joinpath(f"{isbn}.json").open("w", encoding="utf-8") as f:
                json.dump(book_data.model_dump(), f, ensure_ascii=False, indent=4)

        except (ValueError, IndexError) as e:
            logger.error(f"Error retrieving data for ISBN {isbn}: {e}")
            return


def add_books_from_isbn_list(isbn_list: list[ISBN]) -> None:
    """Add multiple books to the database using a list of ISBNs."""
    with db:
        # --- FIX 1: Initialize empty set to prevent UnboundLocalError ---
        isbn_in_db = set()

        # Optimize: Get all existing ISBNs in one fast query
        res = db.run_query("Select isbn from books", as_dataframe=False)
        if res:
            isbn_in_db = {row.get("isbn") for row in res}

        for isbn in isbn_list:
            # Check against our set (O(1) lookup time)
            if isbn in isbn_in_db:
                logger.info(f"ISBN {isbn} already in database. Skipping.")
                continue

            try:
                # Retrieve data
                book_data = retriever.get_book_info(isbn)
                flat_book_data = retriever.flatten_response(book_data, isbn=isbn)

                # Generate summary if missing
                if (
                    not flat_book_data.description
                    or not flat_book_data.description.strip()
                ):
                    book_title = flat_book_data.title
                    book_authors = ", ".join(flat_book_data.authors or [])

                    logger.warning(f"Generating summary for book: {book_title}")
                    summary = book_summary_agent.run_sync(
                        f"{book_title} by {book_authors}"
                    ).output

                    if summary:
                        flat_book_data.description = summary

                # --- MAIN STEP: Add to DB ---
                # Your DB class now handles author deduplication internally!
                db.add_book(flat_book_data)

                # Update local cache so we don't re-add if list has duplicates
                isbn_in_db.add(isbn)

                # Save JSON backup
                with data_folder.joinpath(f"{isbn}.json").open(
                    "w", encoding="utf-8"
                ) as f:
                    json.dump(book_data.model_dump(), f, ensure_ascii=False, indent=4)

            except Exception as e:
                logger.error(f"Error processing ISBN {isbn}: {e}")
                continue