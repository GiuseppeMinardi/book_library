"""Module for managing authors in the book library database."""

from typing import Literal

from fastapi import Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .connection import _get_db
from .models import Author


class AuthorResponse(BaseModel):
    id_: str = Field(..., alias="id")
    message: str
    exists: bool
    status: Literal["ok", "error"]


def get_authors(
    authors_ids: list[str] | None = Query(default=None),
    conn=Depends(_get_db),
) -> dict[str, Author]:
    try:
        query = """
            SELECT id, name, birth_date, death_date, nationality, sex, bio, author_link 
            FROM authors
        """
        params = []

        if authors_ids:
            query += " WHERE id = ANY(%s);"
            params.append(authors_ids)
        else:
            query += ";"

        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

            return {
                str(row[0]): Author(
                    id=str(row[0]),
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch authors.") from e


def add_authors(
    authors_to_add: list[Author] = Body(..., min_length=1),
    conn=Depends(_get_db),
) -> list[AuthorResponse]:
    res = []

    # Pre-fetch all existing authors in a single query to avoid the N+1 problem
    names_to_check = [a.name for a in authors_to_add]

    try:
        # Use conn.transaction() to manage the transaction without closing the connection
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "SELECT id, name FROM authors WHERE name = ANY(%s);",
                (names_to_check,),
            )
            # Create a fast-lookup dictionary of existing authors {name: id}
            existing_authors = {row[1]: str(row[0]) for row in cur.fetchall()}

            for author in authors_to_add:
                if author.name in existing_authors:
                    res.append(
                        AuthorResponse(
                            id=existing_authors[author.name],
                            exists=True,
                            message=f"Author '{author.name}' already exists",
                            status="ok",
                        )
                    )
                    continue

                # Only run INSERT for authors we confirmed don't exist
                cur.execute(
                    """
                    INSERT INTO authors (name, birth_date, death_date, nationality, sex, bio, author_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        author.name,
                        author.birth_date,
                        author.death_date,
                        author.nationality,
                        author.sex,
                        author.bio,
                        author.author_link,
                    ),
                )
                new_id = str(cur.fetchone()[0])
                res.append(
                    AuthorResponse(
                        id=new_id,
                        exists=False,
                        message=f"Author '{author.name}' created successfully",
                        status="ok",
                    )
                )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add authors.") from e


def update_authors(
    authors_to_update: list[Author] = Body(..., min_length=1),
    conn=Depends(_get_db),
) -> list[AuthorResponse]:
    res = []
    try:
        # Use conn.transaction() to manage the transaction without closing the connection
        with conn.transaction(), conn.cursor() as cur:
            for author in authors_to_update:
                cur.execute(
                    """
                    UPDATE authors 
                    SET name = %s, birth_date = %s, death_date = %s, nationality = %s, sex = %s, bio = %s, author_link = %s 
                    WHERE id = %s;
                    """,
                    (
                        author.name,
                        author.birth_date,
                        author.death_date,
                        author.nationality,
                        author.sex,
                        author.bio,
                        author.author_link,
                        author.id,
                    ),
                )

                if cur.rowcount == 0:
                    res.append(
                        AuthorResponse(
                            id=str(author.id),
                            exists=False,
                            message="Author not found",
                            status="error",
                        )
                    )
                else:
                    res.append(
                        AuthorResponse(
                            id=str(author.id),
                            exists=True,
                            message="Updated successfully",
                            status="ok",
                        )
                    )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update authors.") from e


def delete_authors(
    authors_ids: list[str] = Body(..., min_length=1),
    conn=Depends(_get_db),
) -> list[AuthorResponse]:
    try:
        # Use conn.transaction() to manage the transaction without closing the connection
        with conn.transaction(), conn.cursor() as cur:
            cur.execute(
                "DELETE FROM authors WHERE id = ANY(%s) RETURNING id;", (authors_ids,)
            )
            deleted_ids = {str(row[0]) for row in cur.fetchall()}

        return [
            AuthorResponse(
                id=a_id,
                exists=a_id in deleted_ids,
                message="Author deleted successfully"
                if a_id in deleted_ids
                else "Author not found",
                status="ok" if a_id in deleted_ids else "error",
            )
            for a_id in authors_ids
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete authors.") from e