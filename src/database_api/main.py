import os
from typing import Any, Generator

import psycopg
from fastapi import Depends, FastAPI, Query
from pgvector.psycopg import register_vector

app = FastAPI()
DB_URL = os.getenv(key="DATABASE_URL", default="postgresql://admin:secretpassword@localhost:5432/appdb")

def _get_db() -> Generator(psycopg.Connection, None, None):
    conn = psycopg.connect(DB_URL)
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/authors/")
def get_authors(
    # 1. authors must have a default value to be an optional query parameter
    authors: list[str] | None = Query(default=None), 
    # 2. Depends() MUST go in the function signature, not the body
    conn: psycopg.Connection = Depends(_get_db) 
) -> dict[str, dict[str, Any]]:
    
    with conn.cursor() as cur:
        # 3. Separate the execution logic based on whether parameters exist
        if not authors:
            query = "SELECT id, name, nationality FROM authors;"
            cur.execute(query)  # Execute WITHOUT parameters
        else:
            query = """
            SELECT id, name, nationality
            FROM authors
            WHERE name = ANY(%s);
            """
            cur.execute(query, (authors,))  # Execute WITH parameters
            
        rows = cur.fetchall()
        
    return {row[1]: {"id": row[0], "nationality": row[2]} for row in rows}

def main():
    print("Hello from database-api!")


if __name__ == "__main__":
    main()
