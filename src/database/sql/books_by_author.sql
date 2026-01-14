-- Query to get all books written by a specific author
-- Returns book titles, publication dates, page counts, and language

SELECT 
    b.title,
    b.publishedDate,
    b.pageCount,
    b.language,
    b.publisher,
    b.isbn
FROM books b
INNER JOIN book_authors ba ON b.id = ba.book_id
INNER JOIN authors a ON ba.author_id = a.id
WHERE a.name = ?
ORDER BY b.publishedDate DESC;
