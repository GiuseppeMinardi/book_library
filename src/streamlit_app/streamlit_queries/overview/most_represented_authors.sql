SELECT 
    a.name,
    COUNT(ba.book_id) as book_count
FROM authors a
LEFT JOIN book_authors ba ON a.id = ba.author_id
GROUP BY a.id
ORDER BY book_count DESC
LIMIT 10