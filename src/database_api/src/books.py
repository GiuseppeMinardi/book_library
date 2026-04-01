"""Module for managing books in the book library database."""

from typing import Literal

from fastapi import Body, Depends
from pydantic import BaseModel, Field

from .connection import _get_db
from .models import Book


class BookResponse(BaseModel):
    id_: int = Field(
        ..., alias="id", description="Unique identifier for the book in the database"
    )
    message: str = Field(
        ..., description="Status message about the operation performed on the book"
    )
    exists: bool = Field(
        ..., description="Indicates whether the book already exists in the database"
    )
    status: Literal["ok", "error"] = Field(
        ..., description="Overall status of the operation"
    )


def add_books(
    books_to_add: list[Book] = Body(..., min_length=1),  # noqa: B008
    conn=Depends(_get_db),  # noqa: B008
) -> list[BookResponse]:
    res = []
    try:
        # Use a transaction block; it automatically commits if no error occurs
        with conn.cursor() as cur:
            for book in books_to_add:
                cur.execute(
                    "SELECT id FROM books WHERE title = %s OR isbn = %s;",
                    (book.title, book.isbn),
                )
                existing_book = cur.fetchone()

                if existing_book:
                    res.append(
                        BookResponse(
                            id=existing_book[0],
                            exists=True,
                            message=f"Book '{book.title}' already exists",
                            status="ok",
                        )
                    )
                    continue

                cur.execute(
                    """
                        INSERT INTO books (
                            title, publisher, published_date, description,
                            page_count, print_type, language, info_link,
                            small_thumbnail, isbn
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                    (
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
                res.append(
                    BookResponse(
                        id=book_id,
                        exists=False,
                        message=f"Book '{book.title}' created successfully",
                        status="ok",
                    )
                )
        return res  # Success!
    except Exception as e:
        # No need for conn.rollback() if using 'with conn.transaction()'
        raise e
    # REMOVED: finally: conn.close()


def get_books(
    books_ids: list[str] | None = None,
    books_isbn: list[str] | None = None,
    books_titles: list[str] | None = None,
    conn=Depends(_get_db),  # noqa: B008
) -> dict[str, Book | BookResponse]:
    if books_ids is None and books_isbn is None and books_titles is None:
        raise ValueError(
            "At least one of books_ids, books_isbn, or books_titles must be provided"
        )

    try:
        main_query = """
            SELECT id, title, publisher, published_date, description, page_count, print_type, language, info_link, small_thumbnail, isbn
            FROM books
        """
        conditions = []
        params = []

        if books_ids:
            conditions.append("id = ANY(%s)")
            params.append(books_ids)
        if books_isbn:
            conditions.append("isbn = ANY(%s)")
            params.append(books_isbn)
        if books_titles:
            conditions.append("title = ANY(%s)")
            params.append(books_titles)

        query = main_query + " WHERE " + " OR ".join(conditions) + ";"

        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            books_dict: dict[str, Book | BookResponse] = {}
            for row in rows:
                book_id = row[0]
                book_data = Book(
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
                books_dict[str(book_id)] = book_data

        return books_dict
    except Exception as e:
        raise e


def update_books(
    books_to_update: list[Book] = Body(..., min_length=1),  # noqa: B008
    conn=Depends(_get_db),  # noqa: B008
) -> list[BookResponse]:
    res = []
    try:
        with conn.cursor() as cur:
            for book in books_to_update:
                cur.execute("SELECT id FROM books WHERE id = %s;", (book.id,))
                existing_book = cur.fetchone()
                if not existing_book:
                    res.append(
                        BookResponse(
                            id=book.id,
                            exists=False,
                            message="Book not found",
                            status="error",
                        )
                    )
                    continue

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
                        book.id,
                    ),
                )
                res.append(
                    BookResponse(
                        id=book.id,
                        exists=True,
                        message=f"Book '{book.title}' updated successfully",
                        status="ok",
                    )
                )
        conn.commit()
        return res  # Success!
    except Exception as e:
        conn.rollback()
        raise e


def delete_books(
    books_ids: list[str] = Body(..., min_length=1),  # noqa: B008
    books_isbn: list[str] | None = None,
    conn=Depends(_get_db),  # noqa: B008
) -> list[BookResponse]:
    res = []
    try:
        with conn.cursor() as cur:
            for book_id in books_ids:
                cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
                existing_book = cur.fetchone()

                if not existing_book:
                    res.append(
                        BookResponse(
                            id=book_id,
                            exists=False,
                            message="Book not found",
                            status="error",
                        )
                    )
                    continue

                cur.execute("DELETE FROM books WHERE id = %s;", (book_id,))
                res.append(
                    BookResponse(
                        id=book_id,
                        exists=True,
                        message="Book deleted successfully",
                        status="ok",
                    )
                )

                if books_isbn:
                    cur.execute(
                        "DELETE FROM books WHERE isbn = ANY(%s);", (books_isbn,)
                    )
                    res.append(
                        BookResponse(
                            id=book_id,
                            exists=True,
                            message="Books with provided ISBN(s) deleted successfully",
                            status="ok",
                        )
                    )
        conn.commit()
        return res  # Success!
    except Exception as e:
        conn.rollback()
        raise e