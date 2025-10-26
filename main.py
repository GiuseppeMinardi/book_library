import argparse
import sys
from typing import List

import pandas as pd

from src.logger import logger
from src.models.google_sheet import GoogleSheetSettings
from src.populate_authors import populate_authors
from src.populate_books import add_book_from_isbn, add_books_from_isbn_list


def read_isbns_from_sheet() -> List[str]:
    """Read the Google Sheet configured via env/.env and return a list of unique ISBNs.

    Assumes the first column of the sheet contains the ISBN values.
    """
    try:
        sheet_settings = GoogleSheetSettings()
    except Exception as e:
        logger.error(f"Error loading Google Sheet settings: {e}")
        return []

    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_settings.sheet_id}"
        f"/gviz/tq?tqx=out:csv&sheet={sheet_settings.sheet_name}"
    )

    try:
        df = pd.read_csv(filepath_or_buffer=url, dtype={"ISBN": "string"})
    except Exception as e:
        logger.error(f"Error reading Google Sheet CSV: {e}")
        return []

    if df.shape[1] == 0:
        return []

    # take first column as ISBN column, drop NA, strip and deduplicate
    isbns = (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s != ""]
        .unique()
        .tolist()
    )

    return isbns


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Command line tool for dealing with the project"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--from-sheet",
        action="store_true",
        help="Read ISBNs from configured Google Sheet and add books to database",
    )
    group.add_argument(
        "--isbn",
        type=str,
        metavar="ISBN",
        help="Add a single book to the database by ISBN",
    )
    group.add_argument(
        "--fill-authors",
        action="store_true",
        help="Populate missing author information in the database",
    )

    args = parser.parse_args()

    if args.from_sheet:
        isbns = read_isbns_from_sheet()
        if not isbns:
            print("No ISBNs found in sheet or failed to read sheet. Exiting.")
            sys.exit(1)
        logger.info(f"Found {len(isbns)} unique ISBN(s) in sheet. Processing...")
        add_books_from_isbn_list(isbns)
        logger.info("Finished processing sheet ISBNs.")
        return

    if args.isbn:
        isbn = args.isbn.strip()
        if isbn == "":
            logger.warning("Empty ISBN provided.")
            sys.exit(1)
        logger.info(f"Processing ISBN: {isbn}")
        add_book_from_isbn(isbn)
        return

    if args.fill_authors:
        populate_authors()
        return


if __name__ == "__main__":
    main()
