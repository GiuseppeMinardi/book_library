import numpy as np
from pathlib import Path
import pytest
import json
from src import authors, books
from src.models import AuthorEmbedding
from src.authors_embeddings import (
    add_authors_embedding,
    get_embeddings_by_author,
    delete_author_embedding,
    get_incomplete_authors,
)



def test_add_authors_embedding(db_session):
    embedding_examples_path = Path(__file__).parent.joinpath("examples", "author_embeddings.json")
    with embedding_examples_path.open() as f:
        author_embeddings_data = [
            AuthorEmbedding(
                author_id=entry["authorId"],
                model_name=entry["modelName"],
                #random vector of 1536 dimensions for testing purposes
                vector=np.random.rand(1536).tolist(),
                created_at=entry["createdAt"],
            ) 
            for entry in json.load(f)
        ]
    
    res = add_authors_embedding(authors_embeddings_to_add=author_embeddings_data, conn=db_session)
    assert len(res) == len(author_embeddings_data)
    for embedding_res in res:
        assert embedding_res.status == "ok"
        assert embedding_res.author_id is not None
        assert embedding_res.model_name is not None

def test_get_embeddings_by_author(db_session):
    # First, add some embeddings to ensure there is data to retrieve
    ids_in_database = [1,2,3,4]
    retrieved_embeddings = get_embeddings_by_author(authors_id=None, model_name="text-embedding-3-small", conn=db_session)

    assert len(retrieved_embeddings) == len(ids_in_database)
    for retrieved in retrieved_embeddings:
        assert retrieved.status == "ok"
        assert retrieved.author_id in ids_in_database
        assert retrieved.model_name == "text-embedding-3-small"
        assert isinstance(retrieved.vector, list)  # The vector should be a list of floats

def test_delete_author_embedding(db_session):
    # First, add an embedding to ensure there is data to delete
    # add the author and the embedding
    embedding_to_delete = AuthorEmbedding(
        author_id=1,
        model_name="test-model",
        vector=np.random.rand(1536).tolist(),
        created_at="2024-01-01T00:00:00Z",
    )
    add_authors_embedding(authors_embeddings_to_add=[embedding_to_delete], conn=db_session)

    # Now delete the embedding
    delete_response = delete_author_embedding(author_id=1, model_name="test-model", conn=db_session)
    assert delete_response.status == "ok"
    assert delete_response.author_id == 1
    assert delete_response.model_name == "test-model"

    # Verify that the embedding has been deleted
    retrieved_after_deletion = get_embeddings_by_author(authors_id=[1], model_name="test-model", conn=db_session)
    assert len(retrieved_after_deletion) == 1
    assert retrieved_after_deletion[0].status == "error"


def test_get_incomplete_authors(db_session):
    from src.authors import add_authors, Author

    authors = [
        Author(id=0, name="pinco"),
        Author(id=0, name="pallo"),
    ]

    add_authors(authors_to_add=authors, conn=db_session)

    res = get_incomplete_authors(conn=db_session)

    for author in authors:
        assert author.name in [a.name for a in res]
