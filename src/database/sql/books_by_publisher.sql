-- Query to get books published by a specific publisher
-- Shows book details with author information

SELECT 
    b.title,
    b.publishedDate,
    b.pageCount,
    b.language,
    GROUP_CONCAT(a.name, ', ') as authors,
    b.isbn
FROM books b
LEFT JOIN book_authors ba ON b.id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.id
WHERE b.publisher = ?
GROUP BY b.id
ORDER BY b.publishedDate DESC;
