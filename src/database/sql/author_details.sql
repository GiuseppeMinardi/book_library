-- Query to get detailed information about a specific author
-- Includes biography, birth/death dates, and all their books

SELECT 
    a.name,
    a.birth_date,
    a.death_date,
    a.nationality,
    a.sex,
    a.bio,
    COUNT(b.id) as total_books,
    GROUP_CONCAT(DISTINCT b.title, '; ') as books
FROM authors a
LEFT JOIN book_authors ba ON a.id = ba.author_id
LEFT JOIN books b ON ba.book_id = b.id
WHERE a.name = ?
GROUP BY a.id;
