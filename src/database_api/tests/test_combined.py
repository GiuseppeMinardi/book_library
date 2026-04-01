from src.combined import Book, Author, Category, add_book_full, AddFullBooks

def test_combined(db_session):
    full_book_1 = AddFullBooks(
        book=Book(
            id=0,
            title="test",
            publisher="test",
            publishedDate="2020-02-02",
            description="Test Book",
            pageCount=999,
            printType="test",
            language="klingon",
            infoLink=None,
            isbn="348956904823450"
        ),
        authors=[
            Author(
                id=0,
                name="test1",
            ),
            Author(
                id=0,
                name="test2",
            )
        ],
        categories=[
            Category(
                id=0,
                name="Fantasy"
            ),
            Category(
                id=0,
                name="test"
            ),
        ]
    )

    res_full = add_book_full(payload=[full_book_1], conn=db_session)