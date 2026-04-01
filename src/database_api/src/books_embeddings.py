"""CRUD operations for the book embeddings table."""
from typing import Literal

from fastapi import Body, Depends
from pydantic import BaseModel, Field

from .connection import _get_db
from .models import BookEmbedding


class BookEmbeddingResponse(BaseModel):
    status: Literal["ok", "error"] = Field(description="Operation status")
    book_id: int = Field(alias="bookId", description="Reference to the book ID")
    message: str = Field(description="Detailed message about the operation result")
    model_name: str = Field(
        alias="modelName", description="Name of the embedding model"
    )
    vector: list[float] | None = Field(
        default=None, 
        description="The embedding vector if the operation was successful"
    )

def add_books_embedding(
    books_embeddings_to_add: list[BookEmbedding] = Body(..., min_length=1),  # noqa: B008,
    conn=Depends(_get_db),  # noqa: B008
) -> list[BookEmbedding]:
    res = []
    with conn.cursor() as cur:
        for book_embedding in books_embeddings_to_add:
            try:
                cur.execute(
                    """
                    INSERT INTO book_embeddings (book_id, model_name, vector, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (book_id, model_name) DO UPDATE
                    SET vector = EXCLUDED.vector, created_at = EXCLUDED.created_at
                    RETURNING book_id, model_name
                    """,
                    (
                        book_embedding.book_id,
                        book_embedding.model_name,
                        book_embedding.vector,
                        book_embedding.created_at,
                    ),
                )
                inserted_book_embedding = cur.fetchone()
                res.append(
                    BookEmbeddingResponse(
                        status="ok",
                        bookId=inserted_book_embedding[0],
                        modelName=inserted_book_embedding[1],
                        message="Book embedding added/updated successfully",
                        vector=book_embedding.vector,
                    )
                )
            except Exception as e:
                res.append(
                    BookEmbeddingResponse(
                        status="error",
                        bookId=book_embedding.book_id,
                        modelName=book_embedding.model_name,
                        message=f"Failed to add/update book embedding: {str(e)}",
                    )
                )
        conn.commit()
    return res

def get_embeddings_by_book(
    books_id: list[int] = Body(..., min_length=1),  # noqa: B008
    model_name: str = Body(..., description="Name of the embedding model to filter by"),
    conn=Depends(_get_db),  # noqa: B008
) -> list[BookEmbeddingResponse]:
    res = []
    found_ids = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT book_id, model_name, vector
            FROM book_embeddings
            WHERE book_id = ANY(%s) AND model_name = %s
            """,
            (books_id, model_name),
        )
        for book_id, model_name, vector in cur.fetchall():
            found_ids.append(book_id)
            res.append(
                BookEmbeddingResponse(
                    status="ok",
                    bookId=book_id,
                    modelName=model_name,
                    vector=eval(vector),
                    message="Book embedding retrieved successfully",
                )
            )
        for book_id in books_id:
            if book_id not in found_ids:
                res.append(
                    BookEmbeddingResponse(
                        status="error",
                        bookId=book_id,
                        modelName=model_name,
                        message="No embedding found for this book and model",
                    )
                )
    return res

def delete_book_embedding(
    book_id: int = Body(..., description="ID of the book whose embedding should be deleted"),
    model_name: str = Body(..., description="Name of the embedding model to filter by"),
    conn=Depends(_get_db),  # noqa: B008
) -> BookEmbeddingResponse:
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM book_embeddings
            WHERE book_id = %s AND model_name = %s
            RETURNING book_id, model_name
            """,
            (book_id, model_name),
        )
        deleted = cur.fetchone()
        if deleted:
            conn.commit()
            return BookEmbeddingResponse(
                status="ok",
                bookId=deleted[0],
                modelName=deleted[1],
                message="Book embedding deleted successfully",
                vector=None,
            )
        else:
            return BookEmbeddingResponse(
                status="error",
                bookId=book_id,
                modelName=model_name,
                message="No embedding found to delete for this book and model",
            )