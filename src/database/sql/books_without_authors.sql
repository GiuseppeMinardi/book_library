-- Query to find books without associated authors
-- Useful for data quality checks

SELECT 
    b.title,
    b.isbn,
    b.publisher,
    b.publishedDate,
    b.pageCount
FROM books b
WHERE b.id NOT IN (
    SELECT DISTINCT book_id FROM book_authors
)
ORDER BY b.publishedDate DESC;
