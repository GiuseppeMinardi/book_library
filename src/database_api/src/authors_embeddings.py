"""CRUD operations for the book embeddings table."""
from typing import Literal

from fastapi import Body, Depends
from pydantic import BaseModel, Field

from .connection import _get_db
from .models import AuthorEmbedding


class AuthorEmbeddingResponse(BaseModel):
    status: Literal["ok", "error"] = Field(description="Operation status")
    author_id: int = Field(alias="authorId", description="Reference to the author ID")
    message: str = Field(description="Detailed message about the operation result")
    model_name: str = Field(
        alias="modelName", description="Name of the embedding model"
    )
    vector: list[float] | None = Field(
        default=None, 
        description="The embedding vector if the operation was successful"
    )

def add_authors_embedding(
    authors_embeddings_to_add: list[AuthorEmbedding] = Body(..., min_length=1),  # noqa: B008,
    conn=Depends(_get_db),  # noqa: B008
) -> list[AuthorEmbedding]:
    res = []
    with conn.cursor() as cur:
        for author_embedding in authors_embeddings_to_add:
            try:
                cur.execute(
                    """
                    INSERT INTO author_embeddings (author_id, model_name, vector, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (author_id, model_name) DO UPDATE
                    SET vector = EXCLUDED.vector, created_at = EXCLUDED.created_at
                    RETURNING author_id, model_name
                    """,
                    (
                        author_embedding.author_id,
                        author_embedding.model_name,
                        author_embedding.vector,
                        author_embedding.created_at,
                    ),
                )
                inserted_author_embedding = cur.fetchone()
                res.append(
                    AuthorEmbeddingResponse(
                        status="ok",
                        authorId=inserted_author_embedding[0],
                        modelName=inserted_author_embedding[1],
                        message="Author embedding added/updated successfully",
                        vector=author_embedding.vector,
                    )
                )
            except Exception as e:
                res.append(
                    AuthorEmbeddingResponse(
                        status="error",
                        authorId=author_embedding.author_id,
                        modelName=author_embedding.model_name,
                        message=f"Failed to add/update author embedding: {str(e)}",
                    )
                )
        conn.commit()
    return res

def get_embeddings_by_author(
    authors_id: list[int] | None = Body(default=None, min_length=1),  # noqa: B008
    model_name: str = Body(..., description="Name of the embedding model to filter by"),
    conn=Depends(_get_db),  # noqa: B008
) -> list[AuthorEmbeddingResponse]:
    res = []
    found_ids = []
    # no authors id = all embeddings with a specific name
    if authors_id is None:
        base_query = """
        SELECT author_id, model_name, vector
        FROM author_embeddings
        WHERE model_name = %s
        """
        query_params = (model_name,)
    else:
        base_query = """
        SELECT author_id, model_name, vector
        FROM author_embeddings
        WHERE author_id = ANY(%s) AND model_name = %s
        """
        query_params = (authors_id, model_name)

    with conn.cursor() as cur:
        cur.execute(
            base_query,
            query_params
        )
        query_results = cur.fetchall()
        for author_id, model_name, vector in query_results:
            found_ids.append(author_id)
            res.append(
                AuthorEmbeddingResponse(
                    status="ok",
                    authorId=author_id,
                    modelName=model_name,
                    vector=eval(vector),
                    message="Author embedding retrieved successfully",
                )
            )
        if authors_id is None:
            return res 

        for author_id in authors_id:
            if author_id not in found_ids:
                res.append(
                    AuthorEmbeddingResponse(
                        status="error",
                        authorId=author_id,
                        modelName=model_name,
                        message="No embedding found for this author and model",
                    )
                )
    return res

def delete_author_embedding(
    author_id: int = Body(..., description="ID of the author whose embedding should be deleted"),
    model_name: str = Body(..., description="Name of the embedding model to filter by"),
    conn=Depends(_get_db),  # noqa: B008
) -> AuthorEmbeddingResponse:
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM author_embeddings
            WHERE author_id = %s AND model_name = %s
            RETURNING author_id, model_name
            """,
            (author_id, model_name),
        )
        deleted = cur.fetchone()
        if deleted:
            conn.commit()
            return AuthorEmbeddingResponse(
                status="ok",
                authorId=deleted[0],
                modelName=deleted[1],
                message="Author embedding deleted successfully",
                vector=None,
            )
        else:
            return AuthorEmbeddingResponse(
                status="error",
                authorId=author_id,
                modelName=model_name,
                message="No embedding found to delete for this author and model",
            )