"""Module for managing associations between books, authors, and categories in the book library database."""


from fastapi import Depends

from .connection import _get_db


def get_book_categories(book_id: str, conn=Depends(dependency=_get_db)) -> list[int]:  # noqa: B008
    """
    Retrieve categories IDs associated with a specific book.

    Args:
        book_id: ID of the book.
        conn: Database connection.

    Returns
    -------
        List of categories IDs associated with the book.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT category_id
            FROM book_categories
            WHERE book_id = %s
            """,
            (book_id,),
        )
        rows = cur.fetchall()
        return [row[0] for row in rows]

def add_book_categories(
    associations: list[tuple[int, int]], 
    conn=Depends(dependency=_get_db)  # noqa: B008
) -> dict[str, str]:
    """
    Add multiple book-category associations to the database.

    Args:
        associations: A list of tuples containing (book_id, category_id).
        conn: Database connection.

    Returns
    -------
        A dictionary indicating the status of the insertion.
    """
    try:
        with conn.cursor() as cur:
            # executemany is highly optimized for bulk inserts
            cur.executemany(
                """
                INSERT INTO book_categories (book_id, category_id)
                VALUES (%s, %s)
                ON CONFLICT (book_id, category_id) DO NOTHING
                """,
                associations,
            )
        # Don't forget to commit the transaction for INSERTS
        conn.commit()
        
        return {
            "status": "ok", 
            "message": f"Successfully processed {len(associations)} associations."
        }
        
    except Exception as e:
        # Rollback in case of a catastrophic error to keep the DB state clean
        conn.rollback()
        return {
            "status": "error", 
            "message": str(e)
        }