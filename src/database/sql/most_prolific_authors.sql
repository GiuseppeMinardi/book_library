-- Query to find the most prolific authors
-- Shows author name, birth date, nationality, and number of books

SELECT 
    a.name,
    a.birth_date,
    a.nationality,
    COUNT(b.id) as book_count,
    a.author_link
FROM authors a
LEFT JOIN book_authors ba ON a.id = ba.author_id
LEFT JOIN books b ON ba.book_id = b.id
GROUP BY a.id
HAVING book_count > 0
ORDER BY book_count DESC
LIMIT 20;
