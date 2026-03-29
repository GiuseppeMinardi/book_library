"""Database connection management module.

Provides database connection pooling and initialization for the application.
"""

import os
from typing import Generator

import psycopg
from pgvector.psycopg import register_vector

DB_URL = os.getenv(
    key="DATABASE_URL", default="postgresql://admin:secretpassword@localhost:5432/appdb"
)
DB_USER = os.getenv(key="POSTGRES_USER", default="admin")
DB_PASSWORD = os.getenv(key="POSTGRES_PASSWORD", default="secretpassword")
DB_NAME = os.getenv(key="POSTGRES_DB", default="appdb")


def _get_db() -> Generator[psycopg.Connection, None, None]:
    # Prefer a full DATABASE_URL when available (handles container hostnames).
    # Fallback to individual env vars if DB_URL is not provided.
    if DB_URL:
        conn = psycopg.connect(DB_URL)
    else:
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
        )
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()


def get_connection() -> psycopg.Connection:
    """Create and return a new database connection.

    This is a simple helper intended for use by functions that will
    manage the connection lifecycle themselves (for example, API
    endpoint handlers). Use `_get_db` as a FastAPI dependency if you
    want automatic cleanup via `yield`.
    """
    if DB_URL:
        conn = psycopg.connect(DB_URL)
    else:
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
        )
    register_vector(conn)
    return conn
