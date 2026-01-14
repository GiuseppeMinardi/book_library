-- Query to find books with multiple authors
-- Shows collaboration statistics

SELECT 
    b.title,
    COUNT(a.id) as author_count,
    GROUP_CONCAT(a.name, ', ') as authors,
    b.publishedDate,
    b.publisher,
    b.isbn
FROM books b
INNER JOIN book_authors ba ON b.id = ba.book_id
INNER JOIN authors a ON ba.author_id = a.id
GROUP BY b.id
HAVING author_count > 1
ORDER BY author_count DESC, b.publishedDate DESC;
