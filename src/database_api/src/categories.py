"""Module for managing categories in the book library database."""


from fastapi import Depends, Query
from pydantic import BaseModel, Field

from .connection import _get_db


class CategoryResponse(BaseModel):
    id_: int = Field(
        ...,
        alias="id",
        description="Unique identifier for the category in the database",
    )
    message: str = Field(
        ..., description="Status message about the operation performed on the category"
    )
    exists: bool = Field(
        ..., description="Indicates whether the category already exists in the database"
    )
    status: str = Field(..., description="Overall status of the operation")


def get_categories_ids(
    category_names: list[str] | None = Query(default=None),  # noqa: B008
    conn=Depends(_get_db),  # noqa: B008
):
    """
    Retrieve category IDs from the database based on category names.

    Args:
        category_names: Optional list of category names to filter results.
        conn: Database connection.

    Returns
    -------
        List of category IDs corresponding to the provided category names.
    """
    with conn.cursor() as cur:
        if category_names:
            query = """
            SELECT id FROM categories WHERE name = ANY(%s);
            """
            cur.execute(query, (category_names,))
        else:
            query = "SELECT id FROM categories;"
            cur.execute(query)
        category_ids = [row[0] for row in cur.fetchall()]
    return category_ids


# def get_categories(
#     categories_id: list[str] | None = None,
#     query_params: list[str] | None = Query(default=None),
# ) -> dict[str, Category]:
#     """
#     Retrieve categories from the database.
#
#     Args:
#         categories_id: Optional list of category IDs to filter results.
#         query_params: Optional query parameters.
#
#     Returns
#     -------
#         Dictionary with category IDs as keys and Category objects as values.
#     """
#     main_query = """
#     SELECT id, name
#     FROM categories
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             if categories_id:
#                 query = main_query + "WHERE id = ANY(%s);"
#                 cur.execute(query, (categories_id,))
#             else:
#                 cur.execute(main_query + ";")
#             rows = cur.fetchall()
#
#             categories_dict = {row[0]: Category(id=row[0], name=row[1]) for row in rows}
#
#     finally:
#         conn.close()
#
#     return categories_dict
#
#
# def add_category(category: Category) -> dict[str, str | int]:
#     """
#     Add a new category to the database.
#
#     Args:
#         category: Category object with details to insert.
#
#     Returns
#     -------
#         Dictionary with category ID and message about whether the category already exists.
#
#     Raises
#     ------
#         ValueError: If a category with the same name already exists.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT id FROM categories WHERE name = %s;", (category.name,))
#             existing_category = cur.fetchone()
#             if existing_category:
#                 return {"id": existing_category[0], "message": "Category already exists"}
#
#             # insert the new category, id is not provided, it should be autoincremented by the database
#             cur.execute(
#                 """
#                 INSERT INTO categories (name)
#                 VALUES (%s)
#                 RETURNING id;
#                  """,
#                 params=(category.name,),
#             )
#             category_id = cur.fetchone()[0]
#             conn.commit()
#             return {"id": category_id, "message": "Category created successfully"}
#     finally:
#         conn.close()
#
#
# def update_category(
#     category_id: str, category: Category
# ) -> dict[str, str | int]:
#     """
#     Update an existing category's details in the database.
#
#     Args:
#         category_id: ID of the category to update.
#         category: Updated category object.
#
#     Returns
#     -------
#         Dictionary with category ID and message about whether the update was successful.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT id FROM categories WHERE id = %s;", (category_id,))
#             existing_category = cur.fetchone()
#             if not existing_category:
#                 return {"id": category_id, "message": "Category not found"}
#
#             cur.execute(
#                 """
#                 UPDATE categories
#                 SET name = %s
#                 WHERE id = %s;
#                 """,
#                 params=(category.name, category_id),
#             )
#             conn.commit()
#     finally:
#         conn.close()
#
#
# def category_exists(category_id: str ) -> bool:
#     """
#     Check if a category exists in the database.
#
#     Args:
#         category_id: ID of the category to check.
#         conn: Database connection.
#
#     Returns
#     -------
#         True if the category exists, False otherwise.
#     """
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT id FROM categories WHERE id = %s;", (category_id,))
#             return cur.fetchone() is not None
#     finally:
#         conn.close()
#