"""Database connection management module.

Provides database connection pooling and initialization for the application.
"""

import os
from typing import Generator

import psycopg
from pgvector.psycopg import register_vector

DB_USER = os.getenv(key="POSTGRES_USER", default="admin")
DB_PASSWORD = os.getenv(key="POSTGRES_PASSWORD", default="secretpassword")
DB_NAME = os.getenv(key="POSTGRES_DB", default="appdb")
DB_HOST = os.getenv(key="DB_HOST", default="localhost")
DB_PORT = os.getenv(key="DB_PORT", default="5432")

def _get_db() -> Generator[psycopg.Connection, None, None]:
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )
    register_vector(conn)
    try:
        yield conn
    finally:
        # The generator is the ONLY place that should close the connection
        if not conn.closed:
            conn.close()


def get_connection() -> psycopg.Connection:
    """Create and return a new database connection.

    This is a simple helper intended for use by functions that will
    manage the connection lifecycle themselves (for example, API
    endpoint handlers). Use `_get_db` as a FastAPI dependency if you
    want automatic cleanup via `yield`.
    """
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )
    register_vector(conn)
    return conn
