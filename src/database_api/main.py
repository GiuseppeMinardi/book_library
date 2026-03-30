from fastapi import FastAPI, HTTPException

from src import associations_router, authors_router, books_router, categories_router

app = FastAPI()

app.include_router(associations_router)
app.include_router(authors_router)
app.include_router(books_router)
app.include_router(categories_router)

# Register routes at import time so they appear in OpenAPI docs


@app.get("/")
def root():
    return {"message": "Welcome to the Book Library API!"}

@app.get("/health")
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
