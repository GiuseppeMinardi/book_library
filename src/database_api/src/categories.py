"""Module for managing categories in the book library database."""


from fastapi import Query

from .connection import get_connection
from .models import Category


def get_categories(
    categories_id: list[str] | None = None,
    query_params: list[str] | None = Query(default=None),
) -> dict[str, Category]:
    """
    Retrieve categories from the database.

    Args:
        categories_id: Optional list of category IDs to filter results.
        query_params: Optional query parameters.

    Returns
    -------
        Dictionary with category IDs as keys and Category objects as values.
    """
    main_query = """
    SELECT id, name
    FROM categories
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if categories_id:
                query = main_query + "WHERE id = ANY(%s);"
                cur.execute(query, (categories_id,))
            else:
                cur.execute(main_query + ";")
            rows = cur.fetchall()

            categories_dict = {row[0]: Category(id=row[0], name=row[1]) for row in rows}

    finally:
        conn.close()

    return categories_dict


def add_category(category: Category) -> dict[str, str | int]:
    """
    Add a new category to the database.

    Args:
        category: Category object with details to insert.

    Returns
    -------
        Dictionary with category ID and message about whether the category already exists.

    Raises
    ------
        ValueError: If a category with the same name already exists.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM categories WHERE name = %s;", (category.name,))
            existing_category = cur.fetchone()
            if existing_category:
                return {"id": existing_category[0], "message": "Category already exists"}

            # insert the new category, id is not provided, it should be autoincremented by the database
            cur.execute(
                """
                INSERT INTO categories (name)
                VALUES (%s)
                RETURNING id;
                 """,
                params=(category.name,),
            )
            category_id = cur.fetchone()[0]
            conn.commit()
            return {"id": category_id, "message": "Category created successfully"}
    finally:
        conn.close()


def update_category(
    category_id: str, category: Category
) -> dict[str, str | int]:
    """
    Update an existing category's details in the database.

    Args:
        category_id: ID of the category to update.
        category: Updated category object.

    Returns
    -------
        Dictionary with category ID and message about whether the update was successful.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM categories WHERE id = %s;", (category_id,))
            existing_category = cur.fetchone()
            if not existing_category:
                return {"id": category_id, "message": "Category not found"}

            cur.execute(
                """
                UPDATE categories
                SET name = %s
                WHERE id = %s;
                """,
                params=(category.name, category_id),
            )
            conn.commit()
    finally:
        conn.close()


def category_exists(category_id: str ) -> bool:
    """
    Check if a category exists in the database.

    Args:
        category_id: ID of the category to check.
        conn: Database connection.

    Returns
    -------
        True if the category exists, False otherwise.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM categories WHERE id = %s;", (category_id,))
            return cur.fetchone() is not None
    finally:
        conn.close()
