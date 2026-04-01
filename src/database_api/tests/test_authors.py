import pytest

from src.authors import add_authors, delete_authors, get_authors, update_authors
from src.models import Author


def test_add_authors(db_session):
    # 1. Test adding a completely NEW author
    new_author = Author(
        id=999,
        name="Isaac Asimov",
        birth_date="1920-01-02",
        nationality="American",
        sex="M",
        bio="Prolific writer of science fiction.",
    )

    res = add_authors(authors_to_add=[new_author], conn=db_session)
    assert len(res) == 1
    assert res[0].status == "ok"
    assert res[0].exists is False

    # 2. Test the duplicate check using an author already in your DB
    existing_author = Author(
        id=888,
        name="Ursula K. Le Guin",
        birth_date="1929-10-21",
        nationality="American",
        sex="F",
    )

    res_duplicate = add_authors(authors_to_add=[existing_author], conn=db_session)
    assert len(res_duplicate) == 1
    assert res_duplicate[0].status == "ok"
    assert res_duplicate[0].exists is True


def test_get_authors(db_session):
    # Fetch all authors by explicitly passing authors_ids=None
    all_authors = get_authors(authors_ids=None, conn=db_session)

    assert len(all_authors) >= 4  # You have at least 4 seeded authors

    # Dynamically extract IDs for specific checks
    tolkien_id = next(a.id for a in all_authors.values() if a.name == "J.R.R. Tolkien")
    hawking_id = next(a.id for a in all_authors.values() if a.name == "Stephen Hawking")

    # Test get_authors by specific IDs
    authors_res = get_authors(
        authors_ids=[str(tolkien_id), str(hawking_id)], conn=db_session
    )

    assert len(authors_res) == 2
    assert str(tolkien_id) in authors_res
    assert str(hawking_id) in authors_res


def test_update_authors(db_session):
    # Fetch all by explicitly passing authors_ids=None
    all_authors = get_authors(authors_ids=None, conn=db_session)
    isaacson = next(a for a in all_authors.values() if a.name == "Walter Isaacson")

    # Update Walter Isaacson's bio
    isaacson.bio = "Updated: Historian, biographer, and journalist."

    res = update_authors(authors_to_update=[isaacson], conn=db_session)
    assert len(res) == 1
    assert res[0].status == "ok"
    assert res[0].exists is True

    # Verify the update actually persisted in the database
    fetched = get_authors(authors_ids=[str(isaacson.id)], conn=db_session)
    assert (
        fetched[str(isaacson.id)].bio
        == "Updated: Historian, biographer, and journalist."
    )


def test_delete_authors(db_session):
    # Fetch all by explicitly passing authors_ids=None
    all_authors = get_authors(authors_ids=None, conn=db_session)
    hawking_id = next(a.id for a in all_authors.values() if a.name == "Stephen Hawking")

    # Delete the author
    res = delete_authors(authors_ids=[str(hawking_id)], conn=db_session)
    assert len(res) == 1
    assert res[0].status == "ok"
    assert res[0].exists is True

    # Try to get the deleted author
    authors_res = get_authors(authors_ids=[str(hawking_id)], conn=db_session)
    assert len(authors_res) == 0

    # Test delete on an author ID that does not exist
    res_missing = delete_authors(authors_ids=["999999"], conn=db_session)
    assert len(res_missing) == 1
    assert res_missing[0].status == "error"
    assert res_missing[0].exists is False
