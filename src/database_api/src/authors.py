"""Module for managing authors in the book library database."""

from datetime import datetime

from fastapi import Query

from .connection import get_connection
from .models import Author, AuthorEmbedding


def get_authors(
    authors_id: list[str] | None = None,
    query_params: list[str] | None = Query(default=None),
) -> dict[str, dict[str, str]]:
    """
    Retrieve authors from the database.

    Args:
        authors_id: Optional list of author IDs to filter results.
        conn: Database connection.
        query_params: Optional query parameters.

    Returns
    -------
        Dictionary with author IDs as keys and Author objects as values.
    """
    conn = get_connection()
    try:
        main_query = """
    SELECT id, name, birth_date, death_date, nationality, sex, bio, author_link
    FROM authors
    """
        with conn.cursor() as cur:
            if authors_id:
                query = main_query + "WHERE id = ANY(%s);"
                cur.execute(query, (authors_id,))
            else:
                cur.execute(main_query + ";")
            rows = cur.fetchall()

            authors_dict = {
                row[0]: Author(
                    id=row[0],
                    name=row[1],
                    birth_date=row[2],
                    death_date=row[3],
                    nationality=row[4],
                    sex=row[5],
                    bio=row[6],
                    author_link=row[7],
                )
                for row in rows
            }

    finally:
        conn.close()

    return authors_dict


def add_author(author: Author) -> dict[str, str | int]:
    """
    Add a new author to the database.

    Args:
        author: Author object with details to insert.
        conn: Database connection.

    Returns
    -------
        Dictionary with author ID and message about whether the author already exists.

    Raises
    ------
        ValueError: If an author with the same name already exists.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM authors WHERE name = %s;", (author.name,))
            existing_author = cur.fetchone()
            if existing_author:
                return {"id": existing_author[0], "message": "Author already exists"}

            # insert the new author the id is not provided, it should be autoincremented by the database
            cur.execute(
                """
                INSERT INTO authors (name, birth_date, death_date, nationality, sex, bio, author_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                 """,
                params=(
                    author.name,
                    author.birth_date,
                    author.death_date,
                    author.nationality,
                    author.sex,
                    author.bio,
                    author.author_link,
                ),
            )
            author_id = cur.fetchone()[0]
            conn.commit()
            return {"id": author_id, "message": "Author created successfully"}
    finally:
        conn.close()


def update_author(author_id: str, author: Author) -> dict[str, str | int]:
    """
    Update an existing author's details in the database.

    Args:
        author_id: ID of the author to update.
        author: Updated author object.

    Returns
    -------
        Dictionary with author ID and message about whether the update was successful.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM authors WHERE id = %s;", (author_id,))
            existing_author = cur.fetchone()
            if not existing_author:
                return {"id": author_id, "message": "Author not found"}

            cur.execute(
                """
                UPDATE authors
                SET name = %s, birth_date = %s, death_date = %s, nationality = %s, sex = %s, bio = %s, author_link = %s
                WHERE id = %s;
                """,
                params=(
                    author.name,
                    author.birth_date,
                    author.death_date,
                    author.nationality,
                    author.sex,
                    author.bio,
                    author.author_link,
                    author_id,
                ),
            )
            conn.commit()
    finally:
        conn.close()


def author_exists(author_id: str) -> bool:
    """
    Check if an author exists in the database.

    Args:
        author_id: ID of the author to check.

    Returns
    -------
        True if the author exists, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM authors WHERE id = %s;", (author_id,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def add_author_embedding(embedding: AuthorEmbedding):
    """
    Add an embedding for a specific author.

    Args:
        author_id: ID of the author to associate the embedding with.
        embedding: AuthorEmbedding object containing the embedding vector.

    Returns
    -------
        Dictionary with author ID and message about whether the embedding was added successfully.
    """
    conn = get_connection()
    try:
        author_id = embedding.author_id
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM authors WHERE id = %s;", (author_id,))
            existing_author = cur.fetchone()
            if not existing_author:
                return {"id": author_id, "message": "Author not found"}

            cur.execute(
                """
                INSERT INTO author_embeddings (author_id, embedding)
                VALUES (%s, %s);
                """,
                params=(author_id, embedding.vector),
            )
            conn.commit()
            return {"id": author_id, "message": "Embedding added successfully"}
    finally:
        conn.close()


def get_author_embeddings(
    authors_id: list[str] | None = None,
    query_params: list[str] | None = Query(default=None),
) -> dict[str, list[AuthorEmbedding]]:
    """
    Retrieve embeddings for authors.

    Args:
        authors_id: Optional list of author IDs to filter results.
        query_params: Optional query parameters.

    Returns
    -------
        Dictionary mapping author ID -> list of `AuthorEmbedding` objects.
    """
    conn = get_connection()
    try:
        main_query = """
    SELECT author_id, embedding
    FROM author_embeddings
    """
        with conn.cursor() as cur:
            if authors_id:
                cur.execute(main_query + "WHERE author_id = ANY(%s);", (authors_id,))
            else:
                cur.execute(main_query + ";")
            rows = cur.fetchall()

            embeddings: dict[str, list[AuthorEmbedding]] = {}
            for row in rows:
                a_id = row[0]
                vector = row[1]
                emb = AuthorEmbedding(
                    author_id=a_id,
                    model_name="unknown",
                    vector=vector,
                    created_at=datetime.utcnow(),
                )
                embeddings.setdefault(a_id, []).append(emb)

    finally:
        conn.close()

    return embeddings
