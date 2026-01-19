SELECT 
    a.name,
    a.nationality,
    a.birth_date,
    a.death_date,
    COUNT(ba.book_id) as books
FROM authors a
LEFT JOIN book_authors ba ON a.id = ba.author_id
WHERE 1=1