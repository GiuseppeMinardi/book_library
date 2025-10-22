import sqlite3
import uuid
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from ..models.google_books import GoogleBookSlimResponse


class Database:
    def __init__(self, db_location: Path | None = None):
        if db_location is None:
            self.db_location = Path(__file__).parent.joinpath("books.db")
        else:
            self.db_location = db_location

        if not self.db_location.exists():
            self.create_db()

        self.conn = None

    def create_db(self):
        """Create the database file and initializes the tables."""
        print(f"Creating new database at {self.db_location}")
        # The context manager (`with self`) handles connect/disconnect
        with self:
            self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_location)
        except sqlite3.Error as e:
            raise e

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Database connection closed.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def create_tables(self):
        # Connection is now managed by the context manager.
        try:
            cursor = self.conn.cursor()
            # Book Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    publisher TEXT,
                    publishedDate TEXT,
                    description TEXT,
                    pageCount INTEGER,
                    printType TEXT,
                    language TEXT,
                    infoLink TEXT,
                    smallThumbnail TEXT,
                    isbn TEXT UNIQUE NOT NULL
                );
            """)

            # Authors Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS authors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    birth_date TEXT,
                    death_date TEXT,
                    nationality TEXT,
                    sex TEXT,
                    bio TEXT,
                    author_link TEXT
                );
            """)

            # Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
            """)

            # Book-Author Link Table (Many-to-Many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS book_authors (
                    book_id TEXT,
                    author_id TEXT,
                    PRIMARY KEY (book_id, author_id),
                    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
                    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
                );
            """)

            # Book-Category Link Table (Many-to-Many)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS book_categories (
                    book_id TEXT,
                    category_id TEXT,
                    PRIMARY KEY (book_id, category_id),
                    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
                );
            """)
            self.conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def run_query(
        self, query: str, params: tuple = (), as_dataframe: bool = False
    ) -> Union[pd.DataFrame, List[dict], None]:
        if not self.conn:
            print("Cannot run query, no database connection.")
            return None
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)

            # For non-SELECT queries, commit and return
            if not query.strip().upper().startswith("SELECT"):
                self.conn.commit()
                return None

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            if as_dataframe:
                return pd.DataFrame(rows, columns=columns)
            else:
                return [dict(zip(columns, row, strict=False)) for row in rows]

        except sqlite3.Error as e:
            print(f"Error running query: {e}")
            return None

    def add_book(self, book: GoogleBookSlimResponse) -> Optional[str]:
        if not self.conn:
            print("Cannot add book, no database connection.")
            return None

        if not book.title:
            print("Cannot insert book without a title.")
            return None

        try:
            cursor = self.conn.cursor()
            book_id = str(uuid.uuid4())

            # Insert book details, ignore if a book with the same UUID somehow exists.
            cursor.execute(
                """
                INSERT OR IGNORE INTO books
                (id, title, publisher, publishedDate, description, pageCount, printType, language, infoLink, smallThumbnail, isbn)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    book_id,
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

            # Handle authors
            if book.authors:
                for author_name in book.authors:
                    cursor.execute(
                        "SELECT id FROM authors WHERE name = ?", (author_name,)
                    )
                    author_id_row = cursor.fetchone()

                    if author_id_row:
                        author_id = author_id_row[0]
                    else:
                        author_id = str(uuid.uuid4())
                        cursor.execute(
                            "INSERT INTO authors (id, name) VALUES (?, ?)",
                            (author_id, author_name),
                        )

                    cursor.execute(
                        "INSERT OR IGNORE INTO book_authors (book_id, author_id) VALUES (?, ?)",
                        (book_id, author_id),
                    )

            # Handle categories
            if book.categories:
                for category_name in book.categories:
                    cursor.execute(
                        "SELECT id FROM categories WHERE name = ?", (category_name,)
                    )
                    category_id_row = cursor.fetchone()

                    if category_id_row:
                        category_id = category_id_row[0]
                    else:
                        category_id = str(uuid.uuid4())
                        cursor.execute(
                            "INSERT INTO categories (id, name) VALUES (?, ?)",
                            (category_id, category_name),
                        )

                    cursor.execute(
                        "INSERT OR IGNORE INTO book_categories (book_id, category_id) VALUES (?, ?)",
                        (book_id, category_id),
                    )

            self.conn.commit()
            print(f"Successfully added book: {book.title}")
            return book_id

        except sqlite3.Error as e:
            print(f"Error adding book: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def add_author(
        self,
        author_id: str,
        name: str,
        birth_date: Optional[str] = None,
        death_date: Optional[str] = None,
        nationality: Optional[str] = None,
        sex: Optional[str] = None,
        summary: Optional[str] = None,
        author_link: Optional[str] = None,
    ) -> Optional[str]:
        """
        Add or update an author in the database.

        Parameters
        ----------
        author_id : str
            The unique identifier for the author. If None, a new UUID will be generated.
        name : str
            The name of the author.
        birth_date : Optional[str], optional
            The birth date of the author, by default None.
        death_date : Optional[str], optional
            The death date of the author, by default None.
        nationality : Optional[str], optional
            The nationality of the author, by default None.
        sex : Optional[str], optional
            The sex of the author, by default None.
        summary : Optional[str], optional
            A short biography or summary about the author, by default None.
        author_link : Optional[str], optional
            A link to more information about the author, by default None.

        Returns
        -------
        Optional[str]
            The ID of the added or updated author, or None if the operation failed.
        """
        if not self.conn:
            print("Cannot add author, no database connection.")
            return None

        try:
            cursor = self.conn.cursor()
            author_id = author_id or str(uuid.uuid4())

            existing_id = self._find_existing_author(
                cursor=cursor, author_id=author_id, name=name
            )
            if existing_id:
                self._update_author(
                    cursor=cursor,
                    author_id=existing_id,
                    name=name,
                    birth_date=birth_date,
                    death_date=death_date,
                    nationality=nationality,
                    sex=sex,
                    summary=summary,
                    author_link=author_link,
                )
                return existing_id

            self._insert_new_author(
                cursor=cursor,
                author_id=author_id,
                name=name,
                birth_date=birth_date,
                death_date=death_date,
                nationality=nationality,
                sex=sex,
                summary=summary,
                author_link=author_link,
            )
            return author_id

        except sqlite3.IntegrityError as e:
            print(f"Integrity error adding/updating author: {e}")
            if self.conn:
                self.conn.rollback()
            return None
        except sqlite3.Error as e:
            print(f"Error adding/updating author: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def _find_existing_author(self, cursor, author_id: str, name: str) -> Optional[str]:
        cursor.execute("SELECT id FROM authors WHERE id = ?", (author_id,))
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor.execute("SELECT id FROM authors WHERE name = ?", (name,))
        row = cursor.fetchone()
        return row[0] if row else None

    def _update_author(
        self,
        cursor,
        author_id: str,
        name: Optional[str],
        birth_date: Optional[str],
        death_date: Optional[str],
        nationality: Optional[str],
        sex: Optional[str],
        summary: Optional[str],
        author_link: Optional[str],
    ):
        fields = {
            k: v
            for k, v in {
                "name": name,
                "birth_date": birth_date,
                "death_date": death_date,
                "nationality": nationality,
                "sex": sex,
                "bio": summary,
                "author_link": author_link,
            }.items()
            if v is not None
        }

        if fields:
            set_clause = ", ".join([f"{k} = ?" for k in fields])
            params = list(fields.values()) + [author_id]
            sql = f"UPDATE authors SET {set_clause} WHERE id = ?"
            cursor.execute(sql, tuple(params))
            self.conn.commit()
            print(f"Updated author {author_id} ({name})")
        else:
            print(f"No new data provided to update author {author_id} ({name})")

    def _insert_new_author(
        self,
        cursor,
        author_id: str,
        name: str,
        birth_date: Optional[str],
        death_date: Optional[str],
        nationality: Optional[str],
        sex: Optional[str],
        summary: Optional[str],
        author_link: Optional[str],
    ):
        cursor.execute(
            "INSERT INTO authors (id, name, birth_date, death_date, nationality, sex, bio, author_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                author_id,
                name,
                birth_date,
                death_date,
                nationality,
                sex,
                summary,
                author_link,
            ),
        )
        self.conn.commit()
        print(f"Inserted new author {author_id} ({name})")
