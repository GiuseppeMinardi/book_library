from .agent.agent import author_info_agent
from .database.db import Database
from .logger import logger
from .models.agent_models import AuthorInfo

# provider = OllamaProvider(base_url="http://localhost:11434/v1")

_query_authors_to_fill = """
SELECT id, name from authors where sex is null;
"""

db = Database()


def populate_authors() -> None:
    with db as database_session:
        authors_to_fill: dict = database_session.run_query(
            _query_authors_to_fill, as_dataframe=False
        )
        if authors_to_fill is None or len(authors_to_fill) == 0:
            logger.error("No authors found to fill.")
            return

        for author in authors_to_fill:
            try:
                logger.info(f"Processing author: {author['name']}")
                author_name: str = author["name"]
                author_id: str = author["id"]
                author_info: AuthorInfo = author_info_agent.run_sync(author_name).output
                database_session.add_author(
                    author_id=author_id,
                    name=author_name,
                    birth_date=author_info.birth_date,
                    death_date=author_info.death_date,
                    nationality=author_info.nationality,
                    summary=author_info.biography,
                    sex=author_info.sex,
                    author_link=author_info.url,
                )
            except Exception as e:
                logger.error(f"Error processing author {author["name"]}: {e}")
