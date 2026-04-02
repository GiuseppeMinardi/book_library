import numpy as np
from pathlib import Path
import pytest
import json
from src import books
from src.models import BookEmbedding
from src.books_embeddings import (
    add_books_embedding,
    delete_book_embedding,
    get_embeddings_by_book,
    delete_book_embedding,
    get_incomplete_books,
)



def test_add_books_embedding(db_session):
    embedding_examples_path = Path(__file__).parent.joinpath("examples", "book_embeddings.json")
    with embedding_examples_path.open() as f:
        book_embeddings_data = [
            BookEmbedding(
                book_id=entry["bookId"],
                model_name=entry["modelName"],
                #random vector of 1536 dimensions for testing purposes
                vector=np.random.rand(1536).tolist(),
                created_at=entry["createdAt"],
            ) 
            for entry in json.load(f)
        ]
    
    res = add_books_embedding(books_embeddings_to_add=book_embeddings_data, conn=db_session)
    assert len(res) == len(book_embeddings_data)
    for embedding_res in res:
        assert embedding_res.status == "ok"
        assert embedding_res.book_id is not None
        assert embedding_res.model_name is not None

def test_get_embeddings_by_book(db_session):
    # First, add some embeddings to ensure there is data to retrieve
    ids_in_database = [1,2,3,4]
    retrieved_embeddings = get_embeddings_by_book(books_id=ids_in_database, model_name="text-embedding-3-small", conn=db_session)

    assert len(retrieved_embeddings) == len(ids_in_database)
    for retrieved in retrieved_embeddings:
        assert retrieved.book_id in ids_in_database
        assert retrieved.model_name == "text-embedding-3-small"
        assert isinstance(retrieved.vector, list)  # The vector should be a list of floats

def test_delete_book_embedding(db_session):
    # First, add an embedding to ensure there is data to delete
    # add the book and the embedding
    embedding_to_delete = BookEmbedding(
        book_id=1,
        model_name="test-model",
        vector=np.random.rand(1536).tolist(),
        created_at="2024-01-01T00:00:00Z",
    )
    add_books_embedding(books_embeddings_to_add=[embedding_to_delete], conn=db_session)

    # Now delete the embedding
    delete_response = delete_book_embedding(book_id=1, model_name="test-model", conn=db_session)
    assert delete_response.status == "ok"
    assert delete_response.book_id == 1
    assert delete_response.model_name == "test-model"

    # Verify that the embedding has been deleted
    retrieved_after_deletion = get_embeddings_by_book(books_id=[999], model_name="test-model", conn=db_session)
    assert len(retrieved_after_deletion) == 1
    assert retrieved_after_deletion[0].status == "error"


def test_get_incomplete_books(db_session):
    from src.books import add_books, Book

    books = [
        Book(id=0, isbn="pinco", title="pippo"),
        Book(id=0, isbn="pallo", title="pluto"),
    ]

    add_books(books_to_add=books, conn=db_session)

    res = get_incomplete_books(conn=db_session)

    for book in books:
        assert book.isbn in [a.isbn for a in res]
