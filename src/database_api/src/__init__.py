# from fastapi import APIRouter
#
# from src import associations
# from src.associations import (
#     add_book_author,
#     add_book_category,
#     get_book_authors,
#     get_book_categories,
# )
#
# from .authors import (
#     add_author,
#     add_author_embedding,
#     get_author_embeddings,
#     get_authors,
#     update_author,
# )
# from .books import (
#     add_book_embedding,
#     add_books,
#     book_exists,
#     get_books,
#     get_missing_books_embeddings,
#     update_book,
# )
# from .categories import add_category, get_categories, update_category
#
# # AUTHORS =======================================================================================
# authors_router = APIRouter(prefix="/authors", tags=["authors"])
# authors_router.add_api_route("/get_authors", get_authors, methods=["GET"])
# authors_router.add_api_route("/add_author", add_author, methods=["POST"])
# authors_router.add_api_route(
#     "/update_author/{author_id}", update_author, methods=["PUT"]
# )
# authors_router.add_api_route(
#     "/add_author_embedding", add_author_embedding, methods=["POST"]
# )
#
#
# # BOOKS ========================================================================================
# books_router = APIRouter(prefix="/books", tags=["books"])
# books_router.add_api_route("/get_books", get_books, methods=["GET"])
# books_router.add_api_route("/add_books", add_books, methods=["POST"])
# books_router.add_api_route("/update_book/{book_id}", update_book, methods=["PUT"])
# books_router.add_api_route("/add_book_embedding", add_book_embedding, methods=["POST"])
# books_router.add_api_route("/book_exists/{isbn}", book_exists, methods=["GET"])
# books_router.add_api_route(
#     "/missing_books_embeddings", get_missing_books_embeddings, methods=["GET"]
# )
#
# # CATEGORIES ===================================================================================
# categories_router = APIRouter(prefix="/categories", tags=["categories"])
# categories_router.add_api_route("/get_categories", get_categories, methods=["GET"])
# categories_router.add_api_route("/add_category", add_category, methods=["POST"])
# categories_router.add_api_route(
#     "/update_category/{category_id}", update_category, methods=["PUT"]
# )
#
# # ASSOCIATIONS ==================================================================================
# associations_router = APIRouter(prefix="/associations", tags=["associations"])
# associations_router.add_api_route("/add_book_author", add_book_author, methods=["POST"])
# associations_router.add_api_route(
#     "/add_book_category", add_book_category, methods=["POST"]
# )
# associations_router.add_api_route(
#     "/get_book_authors/{book_id}", get_book_authors, methods=["GET"]
# )
# associations_router.add_api_route(
#     "/get_book_categories/{book_id}", get_book_categories, methods=["GET"]
# )
#
