from fastapi import FastAPI, HTTPException

from src import (
    author_embedding_router,
    authors_router,
    book_authors_router,
    book_categories_router,
    book_embedding_router,
    books_router,
)

app = FastAPI()

app.include_router(books_router)
app.include_router(authors_router)
app.include_router(author_embedding_router)
app.include_router(book_embedding_router)
app.include_router(book_categories_router)
app.include_router(book_authors_router)

# Register routes at import time so they appear in OpenAPI docs


@app.get(path="/")
def root():
    return {"message": "Welcome to the Book Library API!"}

@app.get(path="/health")
def health_check():
    """Health check endpoint to verify database connectivity."""
    from src.connection import get_connection
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return {"status": "ok"}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
