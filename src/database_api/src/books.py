"""Module for managing books in the book library database."""

from datetime import datetime

from fastapi import Query

from .connection import get_connection
from .models import Book, BookEmbedding


def get_books(
    books_id: list[str] | None = None,
    query_params: list[str] | None = Query(default=None),
) -> dict[str, dict[str, str]]:
    """
    Retrieve books from the database.

    Args:
        books_id: Optional list of book IDs to filter results.
        conn: Database connection.
        query_params: Optional query parameters.

    Returns
    -------
        Dictionary with book IDs as keys and Book objects as values.
    """
    conn = get_connection()
    try:
        main_query = """
    SELECT id, title, publisher, published_date, description, page_count, print_type, language, info_link, small_thumbnail, isbn
    FROM books
    """
        with conn.cursor() as cur:
            if books_id:
                query = main_query + "WHERE id = ANY(%s);"
                cur.execute(query, (books_id,))
            else:
                cur.execute(main_query + ";")
            rows = cur.fetchall()

            books_dict = {
                row[0]: Book(
                    id=row[0],
                    title=row[1],
                    publisher=row[2],
                    published_date=row[3],
                    description=row[4],
                    page_count=row[5],
                    print_type=row[6],
                    language=row[7],
                    info_link=row[8],
                    small_thumbnail=row[9],
                    isbn=row[10],
                )
                for row in rows
            }

    finally:
        conn.close()

    return books_dict


def add_book(book: Book) -> dict[str, str | int]:
    """
    Add a new book to the database.

    Args:
        book: Book object with details to insert.

    Returns
    -------
        Dictionary with book ID and message about whether the book already exists.

    Raises
    ------
        ValueError: If a book with the same title already exists.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE title = %s;", (book.title,))
            existing_book = cur.fetchone()
            if existing_book:
                return {"id": existing_book[0], "message": "Book already exists"}

            # insert the new book, id is not provided, it should be autoincremented by the database
            cur.execute(
                """
                INSERT INTO books (title, publisher, published_date, description, page_count, print_type, language, info_link, small_thumbnail, isbn)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                 """,
                params=(
                    book.title,
                    book.publisher,
                    book.published_date,
                    book.description,
                    book.page_count,
                    book.print_type,
                    book.language,
                    book.info_link,
                    book.small_thumbnail,
                    book.isbn,
                ),
            )
            book_id = cur.fetchone()[0]
            conn.commit()
            return {"id": book_id, "message": "Book created successfully"}
    finally:
        conn.close()


def update_book(book_id: str, book: Book) -> dict[str, str | int]:
    """
    Update an existing book's details in the database.

    Args:
        book_id: ID of the book to update.
        book: Updated book object.
        conn: Database connection.

    Returns
    -------
        Dictionary with book ID and message about whether the update was successful.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
            existing_book = cur.fetchone()
            if not existing_book:
                return {"id": book_id, "message": "Book not found"}

            cur.execute(
                """
                UPDATE books
                SET title = %s, publisher = %s, published_date = %s, description = %s, page_count = %s, print_type = %s, language = %s, info_link = %s, small_thumbnail = %s, isbn = %s
                WHERE id = %s;
                """,
                params=(
                    book.title,
                    book.publisher,
                    book.published_date,
                    book.description,
                    book.page_count,
                    book.print_type,
                    book.language,
                    book.info_link,
                    book.small_thumbnail,
                    book.isbn,
                    book_id,
                ),
            )
            conn.commit()
    finally:
        conn.close()


def book_exists(book_id: str) -> bool:
    """
    Check if a book exists in the database.

    Args:
        book_id: ID of the book to check.

    Returns
    -------
        True if the book exists, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def add_book_embedding(embedding: BookEmbedding):
    """
    Add an embedding for a specific book.

    Args:
        embedding: BookEmbedding object containing the embedding vector.
        conn: Database connection.

    Returns
    -------
        Dictionary with book ID and message about whether the embedding was added successfully.
    """
    book_id = embedding.book_id
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
            existing_book = cur.fetchone()
            if not existing_book:
                return {"id": book_id, "message": "Book not found"}

            cur.execute(
                """
                INSERT INTO book_embeddings (book_id, embedding)
                VALUES (%s, %s);
                """,
                params=(book_id, embedding.vector),
            )
            conn.commit()
            return {"id": book_id, "message": "Embedding added successfully"}
    finally:
        conn.close()


def get_book_embeddings(
    books_id: list[str] | None = None,
    query_params: list[str] | None = Query(default=None),
) -> dict[str, list[BookEmbedding]]:
    """
    Retrieve embeddings for books.

    Args:
        books_id: Optional list of book IDs to filter results.
        query_params: Optional query parameters.

    Returns
    -------
        Dictionary mapping book ID -> list of `BookEmbedding` objects.
    """
    conn = get_connection()
    try:
        main_query = """
    SELECT book_id, embedding
    FROM book_embeddings
    """

        with conn.cursor() as cur:
            if books_id:
                cur.execute(main_query + "WHERE book_id = ANY(%s);", (books_id,))
            else:
                cur.execute(main_query + ";")
            rows = cur.fetchall()

            embeddings: dict[str, list[BookEmbedding]] = {}
            for row in rows:
                b_id = row[0]
                vector = row[1]
                emb = BookEmbedding(
                    book_id=b_id,
                    model_name="unknown",
                    vector=vector,
                    created_at=datetime.utcnow(),
                )
                embeddings.setdefault(b_id, []).append(emb)

    finally:
        conn.close()

    return embeddings


def get_missing_books_embeddings() -> list[Book]:

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM books
                WHERE id NOT IN (SELECT book_id FROM book_embeddings);
                """
            )
            rows = cur.fetchall()
            return [Book(*row) for row in rows]
    finally:
        conn.close()
