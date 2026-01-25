import pickle

import ollama

from .database.db import Database
from .logger import logger
from .models.ollama_models import OllamaEmbeddingSettings

settings = OllamaEmbeddingSettings()
db = Database()


def populate_embeddings():
    with db:
        logger.info("Starting embedding population process.")
        books = db.run_query(
            "SELECT id, description FROM books WHERE description IS NOT NULL",
            as_dataframe=True,
        )
        logger.info(f"Found {len(books)} books with descriptions to embed.")
        descriptions = books["description"].tolist()
        response = ollama.embed(model=settings.model_name, input=descriptions)

        embeddings = response.embeddings
        logger.info(f"Received {len(embeddings)} embeddings from Ollama.")

        for i, embedding in enumerate(embeddings):
            book_id = books.iloc[i]["id"]
            db.add_book_embedding(
                book_id=book_id,
                model_name=settings.model_name,
                embedding_vector=embedding,
            )
            logger.info(f"Stored embedding for book ID: {book_id}")

        authors = db.run_query(
            "SELECT id, bio as biography FROM authors WHERE bio IS NOT NULL",
            as_dataframe=True,
        )
        biographies = authors["biography"].tolist()
        logger.info(f"Found {len(authors)} authors with biographies to embed.")
        response = ollama.embed(model=settings.model_name, input=biographies)
        embeddings = response.embeddings
        logger.info(f"Received {len(embeddings)} embeddings from Ollama for authors.")
        for i, embedding in enumerate(embeddings):
            author_id = authors.iloc[i]["id"]
            db.add_author_embedding(
                author_id=author_id,
                model_name=settings.model_name,
                embedding_vector=embedding,
            )
            logger.info(f"Stored embedding for author ID: {author_id}")

        logger.info("Completed embedding population process.")
