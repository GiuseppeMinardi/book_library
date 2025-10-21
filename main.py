import json
from pathlib import Path

from dotenv import load_dotenv

import pandas as pd

from src.book_api import GoogleBookRetriever
from src.database.db import Database
from src.models.google_sheet import GoogleSheetSettings

load_dotenv()

db = Database()
sheet_settings = GoogleSheetSettings()

data_folder = Path(__file__).parent.joinpath("data", "isbn_response")
data_folder.mkdir(parents=True, exist_ok=True)

retriever = GoogleBookRetriever()
# 3. Construct the URL
url = f"https://docs.google.com/spreadsheets/d/{sheet_settings.sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_settings.sheet_name}"

# 4. Read into a DataFrame
isbn_list = (
    pd.read_csv(filepath_or_buffer=url, dtype={"ISBN": "string"}).iloc[:, 0].tolist()
)

with db:
    res = db.run_query("Select isbn from books", as_dataframe=False)
    if res is not None and isinstance(res, list):
        isbn_in_df = [row.get("isbn") for row in res]

    for isbn in isbn_list:
        if isbn in isbn_in_df:
            print(f"ISBN {isbn} already in database. Skipping.")
            continue
        try:
            book_data = retriever.get_book_info(isbn)
            flat_book_data = retriever.flatten_response(book_data, isbn=isbn)
            db.add_book(flat_book_data)
            with data_folder.joinpath(f"{isbn}.json").open("w", encoding="utf-8") as f:
                json.dump(book_data.model_dump(), f, ensure_ascii=False, indent=4)
        except (ValueError, IndexError) as e:
            print(f"Error retrieving data for ISBN {isbn}: {e}")
            continue

#
# for isbn in isbn_list:
#
#     try:
#         book_data = retriever.get_book_info(isbn).model_dump()
#     except (ValueError, IndexError) as e:
#         print(f"Error retrieving data for ISBN {isbn}: {e}")
#         continue
#     with data_folder.joinpath(f"{isbn}.json").open("w", encoding="utf-8") as f:
#         json.dump(book_data, f, ensure_ascii=False, indent=4)
# #
