from fastapi import FastAPI

from src.associations import (
    add_book_author,
    add_book_category,
    get_book_authors,
    get_book_categories,
)
from src.authors import add_author, add_author_embedding, get_authors, update_author
from src.books import (
    add_book,
    add_book_embedding,
    get_books,
    get_missing_books_embeddings,
    update_book,
)
from src.categories import add_category, get_categories, update_category
from src.connection import get_connection

app = FastAPI()

# Register routes at import time so they appear in OpenAPI docs
app.add_api_route("/get_books", get_books, methods=["GET"])
app.add_api_route("/add_book", add_book, methods=["POST"])
app.add_api_route("/update_book/{book_id}", update_book, methods=["PUT"])
app.add_api_route("/add_book_embedding", add_book_embedding, methods=["POST"])
app.add_api_route("/get_authors", get_authors, methods=["GET"])
app.add_api_route("/add_author", add_author, methods=["POST"])
app.add_api_route("/update_author/{author_id}", update_author, methods=["PUT"])
app.add_api_route("/add_author_embedding", add_author_embedding, methods=["POST"])
app.add_api_route("/get_categories", get_categories, methods=["GET"])
app.add_api_route("/add_category", add_category, methods=["POST"])
app.add_api_route("/update_category/{category_id}", update_category, methods=["PUT"])
app.add_api_route("/add_book_author", add_book_author, methods=["POST"])
app.add_api_route("/add_book_category", add_book_category, methods=["POST"])
app.add_api_route("/get_book_authors/{book_id}", get_book_authors, methods=["GET"])
app.add_api_route(
    "/get_book_categories/{book_id}", get_book_categories, methods=["GET"]
)
app.add_api_route(
    "/missing_books_embeddings", get_missing_books_embeddings, methods=["GET"]
)


@app.get("/health")
def health_check():
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return {"status": "ok"}
        finally:
            conn.close()
    except Exception as e:
        return {"status": "error", "message": str(e)}
