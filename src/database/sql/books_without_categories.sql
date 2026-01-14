-- Query to find books without associated categories
-- Useful for data quality checks

SELECT 
    b.title,
    b.isbn,
    b.publisher,
    GROUP_CONCAT(a.name, ', ') as authors,
    b.publishedDate
FROM books b
LEFT JOIN book_authors ba ON b.id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.id
WHERE b.id NOT IN (
    SELECT DISTINCT book_id FROM book_categories
)
GROUP BY b.id
ORDER BY b.publishedDate DESC;
