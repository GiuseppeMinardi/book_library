-- Query to get the longest books in the library
-- Shows top 20 books ordered by page count

SELECT 
    b.title,
    b.pageCount,
    b.publisher,
    b.publishedDate,
    b.language,
    GROUP_CONCAT(a.name, ', ') as authors
FROM books b
LEFT JOIN book_authors ba ON b.id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.id
WHERE b.pageCount IS NOT NULL
GROUP BY b.id
ORDER BY b.pageCount DESC
LIMIT 20;
