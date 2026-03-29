"""Module for managing associations between books, authors, and categories in the book library database."""

from .connection import get_connection


def get_book_authors(book_id: str) -> list[str]:
    """
    Retrieve author IDs associated with a specific book.

    Args:
        book_id: ID of the book.
        conn: Database connection.

    Returns
    -------
        List of author IDs associated with the book.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT author_id FROM book_authors WHERE book_id = %s;", (book_id,)
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()


def get_book_categories(book_id: str) -> list[str]:
    """
    Retrieve category IDs associated with a specific book.

    Args:
        book_id: ID of the book.
        conn: Database connection.

    Returns
    -------
        List of category IDs associated with the book.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT category_id FROM book_categories WHERE book_id = %s;", (book_id,)
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()


def add_book_author(book_id: str, author_id: str) -> dict[str, str]:
    """
    Add an association between a book and an author.

    Args:
        book_id: ID of the book.
        author_id: ID of the author.
        conn: Database connection.

    Returns
    -------
        Dictionary with message about whether the association was added successfully.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if book exists
            cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
            if not cur.fetchone():
                return {"message": "Book not found"}

            # Check if author exists
            cur.execute("SELECT id FROM authors WHERE id = %s;", (author_id,))
            if not cur.fetchone():
                return {"message": "Author not found"}

            # Check if association already exists
            cur.execute(
                "SELECT 1 FROM book_authors WHERE book_id = %s AND author_id = %s;",
                (book_id, author_id),
            )
            if cur.fetchone():
                return {"message": "Association already exists"}

            # Insert the association
            cur.execute(
                """
                INSERT INTO book_authors (book_id, author_id)
                VALUES (%s, %s);
                """,
                params=(book_id, author_id),
            )
            conn.commit()
            return {"message": "Association added successfully"}
    finally:
        conn.close()


def add_book_category(book_id: str, category_id: str) -> dict[str, str]:
    """
    Add an association between a book and a category.

    Args:
        book_id: ID of the book.
        category_id: ID of the category.
        conn: Database connection.

    Returns
    -------
        Dictionary with message about whether the association was added successfully.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if book exists
            cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
            if not cur.fetchone():
                return {"message": "Book not found"}

            # Check if category exists
            cur.execute("SELECT id FROM categories WHERE id = %s;", (category_id,))
            if not cur.fetchone():
                return {"message": "Category not found"}

            # Check if association already exists
            cur.execute(
                "SELECT 1 FROM book_categories WHERE book_id = %s AND category_id = %s;",
                (book_id, category_id),
            )
            if cur.fetchone():
                return {"message": "Association already exists"}

            # Insert the association
            cur.execute(
                """
                INSERT INTO book_categories (book_id, category_id)
                VALUES (%s, %s);
                """,
                params=(book_id, category_id),
            )
            conn.commit()
            return {"message": "Association added successfully"}
    finally:
        conn.close()
