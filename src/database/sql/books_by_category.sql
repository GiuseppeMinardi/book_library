-- Query to get all books in a specific category
-- Returns book details with author information

SELECT 
    b.title,
    b.publisher,
    b.publishedDate,
    b.pageCount,
    GROUP_CONCAT(a.name, ', ') as authors,
    b.language,
    b.isbn
FROM books b
INNER JOIN book_categories bc ON b.id = bc.book_id
INNER JOIN categories c ON bc.category_id = c.id
LEFT JOIN book_authors ba ON b.id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.id
WHERE c.name = ?
GROUP BY b.id
ORDER BY b.publishedDate DESC;
