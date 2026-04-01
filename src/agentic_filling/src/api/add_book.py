import requests

from ..agents import get_author_info_agent, get_book_summary_agent
from ..book_api import GoogleBookRetriever
from ..conf import Settings

settings = Settings()
author_info_agent = get_author_info_agent()
book_summary_agent = get_book_summary_agent()
book_retriever = GoogleBookRetriever()

def add_book_by_isbn(isbn: str) -> dict:
    api_endpoint = settings.db_api_endpoint

    # Check if the book already exists in the database
    response = requests.get(f"{api_endpoint}/books/book_exists/{isbn}")
    if response.status_code == 200 and response.json().get("exists", False):
        return {"error": f"Book with ISBN {isbn} already exists in the database."}
    
    # Retrieve book data from Google Books API
    try:
        book_data = book_retriever.get_book_info(isbn=isbn)
    except Exception as e:
        return {"error": f"Failed to retrieve book data form google books: {str(e)}"}

    book_title = book_data.volume_info.title
    authors_list = book_data.volume_info.authors or []
    book_authors = ", ".join(authors_list)

    flat_book_data = book_retriever.flatten_response(book_data, isbn=isbn)

    book_description = flat_book_data.description
    if not book_description or not book_description.strip():
        try:
            summary_response = book_summary_agent.run_sync(
                f"{book_title} by {book_authors}"
            ).output
            if summary_response is None or len(summary_response) == 0:
                #in future log a warning here
                pass
            flat_book_data.description = summary_response
        except Exception as e:
            return {"error": f"Failed to generate book summary: {str(e)}"}
    
    
