from fastapi import APIRouter

from .authors import add_authors, delete_authors, get_authors, update_authors
from .authors_embeddings import (
    add_authors_embedding,
    delete_author_embedding,
    get_embeddings_by_author,
)
from .book_authors import add_book_authors, get_book_authors
from .book_categories import add_book_categories, get_book_categories
from .books import add_books, delete_books, get_books, update_books
from .books_embeddings import (
    add_books_embedding,
    delete_book_embedding,
    get_embeddings_by_book,
)
from .combined import add_book_full

# ---------------------------------------------------------
# Book Categories Router (e.g., Many-to-Many Mapping)
# ---------------------------------------------------------
book_categories_router = APIRouter(prefix="/book_categories", tags=["Book", "Category"])

book_categories_router.add_api_route(
    path="/", endpoint=add_book_categories, tags=["Create"], methods=["POST"]
)

book_categories_router.add_api_route(
    path="/", endpoint=get_book_categories, tags=["Get"], methods=["GET"]
)


# ---------------------------------------------------------
# Book Authors Router (e.g., Many-to-Many Mapping)
# ---------------------------------------------------------
book_authors_router = APIRouter(prefix="/book_authors", tags=["Book", "Author"])

book_authors_router.add_api_route(
    path="/", endpoint=add_book_authors, tags=["Create"], methods=["POST"]
)

book_authors_router.add_api_route(
    path="/", endpoint=get_book_authors, tags=["Get"], methods=["GET"]
)


# ---------------------------------------------------------
# Author Embeddings Router
# ---------------------------------------------------------
author_embedding_router = APIRouter(
    prefix="/authors_embeddings", tags=["Author", "Embeddings"]
)

author_embedding_router.add_api_route(
    path="/", endpoint=add_authors_embedding, tags=["Create"], methods=["POST"]
)

author_embedding_router.add_api_route(
    path="/by_author/",
    endpoint=get_embeddings_by_author,
    tags=["Get"],
    methods=["GET"],
)

author_embedding_router.add_api_route(
    path="/",
    endpoint=delete_author_embedding,
    tags=["Delete"],
    methods=["DELETE"],
)


# ---------------------------------------------------------
# Book Embeddings Router
# ---------------------------------------------------------
book_embedding_router = APIRouter(
    prefix="/books_embeddings", tags=["Book", "Embeddings"]
)

book_embedding_router.add_api_route(
    path="/", endpoint=add_books_embedding, tags=["Create"], methods=["POST"]
)

book_embedding_router.add_api_route(
    path="/by_book/",
    endpoint=get_embeddings_by_book,
    tags=["Get"],
    methods=["GET"],
)

book_embedding_router.add_api_route(
    path="/",
    endpoint=delete_book_embedding,
    tags=["Delete"],
    methods=["DELETE"],
)


# ---------------------------------------------------------
# Books Router
# ---------------------------------------------------------
books_router = APIRouter(prefix="/books", tags=["Book"])

books_router.add_api_route(
    path="/", endpoint=add_books, tags=["Create"], methods=["POST"]
)

books_router.add_api_route(path="/", endpoint=get_books, tags=["Get"], methods=["GET"])

books_router.add_api_route(
    path="/", endpoint=update_books, tags=["Put"], methods=["PUT"]
)

books_router.add_api_route(
    path="/",
    endpoint=delete_books,
    tags=["Delete"],
    methods=["DELETE"],
)


# ---------------------------------------------------------
# Authors Router
# ---------------------------------------------------------
authors_router = APIRouter(prefix="/authors", tags=["Author"])

authors_router.add_api_route(
    path="/", endpoint=add_authors, tags=["Create"], methods=["POST"]
)

authors_router.add_api_route(
    path="/", endpoint=get_authors, tags=["Get"], methods=["GET"]
)

authors_router.add_api_route(
    path="/", endpoint=update_authors, tags=["Put"], methods=["PUT"]
)

authors_router.add_api_route(
    path="/",
    endpoint=delete_authors,
    tags=["Delete"],
    methods=["DELETE"],
)

complex_router = APIRouter(prefix="/complex", tags=["Book", "Author", "Category"])
complex_router.add_api_route(
    path="/", endpoint=add_book_full, tags=["Post"], methods=["POST"]
)