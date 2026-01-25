"""Database handling module."""

import pickle
import sqlite3
import uuid
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from ..logger import logger
from ..models.google_books import GoogleBookSlimResponse
from ..models.project_paths import ProjectPathsSettings

project_paths = ProjectPathsSettings()


class Database:
    """Class to connect and handle the sl=qllite database."""

    def __init__(self, db_location: Path | None = None):
        if db_location is None:
            self.db_location = project_paths.database_path
        else:
            self.db_location = db_location

        if not self.db_location.exists():
            self.create_db()

        self.conn = None
        self.connect()

    def create_db(self):
        """Create the database file and initializes the tables."""
        logger.info(f"Creating new database at {self.db_location}")
        # The context manager (`with self`) handles connect/disconnect
        with self:
            self.create_tables()

    def connect(self):
        """Connect to the Database."""
        try:
            logger.info(f"Connecting to database at {self.db_location}")
            self.conn = sqlite3.connect(self.db_location, check_same_thread=False)
        except sqlite3.Error as e:
            raise e

    def disconnect(self):
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed.")

    def __enter__(self):
        """Enter the connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the connection."""
        self.disconnect()

    def create_tables(self):
        """Create the necessary tables in the database."""
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

            # Embeddings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS book_embeddings (
                    book_id TEXT,
                    model_name TEXT,
                    vector BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (book_id, model_name),
                    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
                );
            """)
            self.conn.commit()

            # author embeddings
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS author_embeddings (
                    author_id TEXT,
                    model_name TEXT,
                    vector BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (author_id, model_name),
                    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
                );
            """
            )
            logger.info("Tables created successfully.")
        except sqlite3.Error as e:
            logger.info(f"Error creating tables: {e}")

    def run_query(
        self, query: str, params: tuple = (), as_dataframe: bool = False
    ) -> Union[pd.DataFrame, List[dict], None]:
        """
        Execute a SQL query on the database.

        Parameters
        ----------
        query : str
            The SQL query to execute.
        params : tuple, optional
            The parameters to bind to the query, by default ().
        as_dataframe : bool, optional
            If True, return the results as a pandas DataFrame. Otherwise, return a list of dictionaries, by default False.

        Returns
        -------
        Union[pd.DataFrame, List[dict], None]
            The query results as a DataFrame or a list of dictionaries for SELECT queries.
            Returns None for non-SELECT queries or if the connection is not established.

        Raises
        ------
        sqlite3.Error
            If an error occurs while executing the query.
        """
        if not self.conn:
            logger.info("Cannot run query, no database connection.")
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
            raise sqlite3.Error(f"Error running query: {e}") from e

    def add_book(self, book: GoogleBookSlimResponse) -> Optional[str]:
        """
        Add a book to the database, including its authors and categories.

        Parameters
        ----------
        book : GoogleBookSlimResponse
            The book details to be added.

        Returns
        -------
        Optional[str]
            The ID of the added book, or None if the operation failed.
        """
        if not self.conn:
            logger.info("Cannot add book, no database connection.")
            return None

        if not book.title:
            logger.info("Cannot insert book without a title.")
            return None

        try:
            cursor = self.conn.cursor()
            book_id = str(uuid.uuid4())

            self._insert_book(cursor, book_id, book)
            self._handle_authors(cursor, book_id, book.authors)
            self._handle_categories(cursor, book_id, book.categories)

            self.conn.commit()
            logger.info(f"Successfully added book: {book.title}")
            return book_id

        except sqlite3.Error as e:
            logger.info(f"Error adding book: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def _insert_book(self, cursor, book_id: str, book: GoogleBookSlimResponse):
        """Insert the book details into the database."""
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

    def _handle_authors(self, cursor, book_id: str, authors: Optional[List[str]]):
        """Handle the authors of the book."""
        if not authors:
            return

        for original_name in authors:
            # FIX: Strip whitespace once, use 'clean_name' everywhere
            clean_name = original_name.strip()
            
            # STEP 1: Check if cleaned author name exists
            cursor.execute(
                "SELECT id FROM authors WHERE name = ?", (clean_name,)
            )
            author_id_row = cursor.fetchone()

            # STEP 2: Reuse existing ID
            if author_id_row:
                author_id = author_id_row[0]
            # STEP 3: Create new author with the CLEAN name
            else:
                author_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO authors (id, name) VALUES (?, ?)",
                    (author_id, clean_name),
                )

            # Link Book to Author
            cursor.execute(
                "INSERT OR IGNORE INTO book_authors (book_id, author_id) VALUES (?, ?)",
                (book_id, author_id),
            )

    def _handle_categories(self, cursor, book_id: str, categories: Optional[List[str]]):
        """Handle the categories of the book."""
        if not categories:
            return

        for category_name in categories:
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
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
            logger.info("Cannot add author, no database connection.")
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
            logger.error(f"Integrity error adding/updating author: {e}")
            if self.conn:
                self.conn.rollback()
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding/updating author: {e}")
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
            logger.info(f"Updated author {author_id} ({name})")
        else:
            logger.info(f"No new data provided to update author {author_id} ({name})")

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
        logger.info(f"Inserted new author {author_id} ({name})")

    def add_author_embedding(
        self, author_id: str, embedding_vector: List[float], model_name: str = "default"
    ):
        """
        Add or update an embedding for a specific author.

        Parameters
        ----------
        author_id : str
            The ID of the author.
        embedding_vector : List[float]
            The embedding vector (list of floats).
        model_name : str, optional
            The name of the model used to generate the embedding, by default "default".
        """
        if not self.conn:
            logger.info("Cannot add embedding, no database connection.")
            return

        try:
            # Serialize the vector to bytes using pickle for storage as BLOB
            vector_blob = pickle.dumps(embedding_vector)

            cursor = self.conn.cursor()
            # Upsert logic: Update if the author_id+model_name combination exists
            cursor.execute(
                """
                INSERT INTO author_embeddings (author_id, model_name, vector)
                VALUES (?, ?, ?)
                ON CONFLICT(author_id, model_name)
                DO UPDATE SET vector=excluded.vector, created_at=CURRENT_TIMESTAMP
                """,
                (author_id, model_name, vector_blob),
            )
            self.conn.commit()
            logger.info(
                f"Added embedding for author {author_id} using model {model_name}"
            )

        except sqlite3.Error as e:
            logger.error(f"Error adding embedding: {e}")
            if self.conn:
                self.conn.rollback()

    def add_book_embedding(
        self, book_id: str, embedding_vector: List[float], model_name: str = "default"
    ):
        """
        Add or update an embedding for a specific book description.

        Parameters
        ----------
        book_id : str
            The ID of the book.
        embedding_vector : List[float]
            The embedding vector (list of floats).
        model_name : str, optional
            The name of the model used to generate the embedding, by default "default".
        """
        if not self.conn:
            logger.info("Cannot add embedding, no database connection.")
            return

        try:
            # Serialize the vector to bytes using pickle for storage as BLOB
            vector_blob = pickle.dumps(embedding_vector)

            cursor = self.conn.cursor()
            # Upsert logic: Update if the book_id+model_name combination exists
            cursor.execute(
                """
                INSERT INTO book_embeddings (book_id, model_name, vector)
                VALUES (?, ?, ?)
                ON CONFLICT(book_id, model_name)
                DO UPDATE SET vector=excluded.vector, created_at=CURRENT_TIMESTAMP
                """,
                (book_id, model_name, vector_blob),
            )
            self.conn.commit()
            logger.info(f"Added embedding for book {book_id} using model {model_name}")

        except sqlite3.Error as e:
            logger.error(f"Error adding embedding: {e}")
            if self.conn:
                self.conn.rollback()

    def get_embeddings(
        self, model_name: str = "default", as_dataframe: bool = True
    ) -> Union[pd.DataFrame, dict[str, List[float]], None]:
        """
        Retrieve all embeddings for a specific model.

        Parameters
        ----------
        model_name : str, optional
            The name of the model to filter by, by default "default".
        as_dataframe : bool, optional
            If True, return a pandas DataFrame. If False, return a dictionary {book_id: vector}, by default True.

        Returns
        -------
        Union[pd.DataFrame, dict[str, List[float]], None]
            A DataFrame with columns ['book_id', 'vector'] or a dictionary mapping book_id to the embedding list.
        """
        if not self.conn:
            logger.info("Cannot get embeddings, no database connection.")
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT book_id, vector FROM embeddings WHERE model_name = ?",
                (model_name,),
            )
            rows = cursor.fetchall()

            if not rows:
                return pd.DataFrame() if as_dataframe else {}

            # Deserialize the BLOBs back into lists
            data = {book_id: pickle.loads(vector_blob) for book_id, vector_blob in rows}

            if as_dataframe:
                # Create a DataFrame with two columns: book_id and vector (containing the list)
                df_ = pd.DataFrame(list(data.items()), columns=["book_id", "vector"])
                return df_

            return data

        except sqlite3.Error as e:
            logger.error(f"Error retrieving embeddings: {e}")
            return None
