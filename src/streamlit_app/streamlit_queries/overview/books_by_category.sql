SELECT 
    c.name,
    COUNT(bc.book_id) as count
FROM categories c
LEFT JOIN book_categories bc ON c.id = bc.category_id
GROUP BY c.id
ORDER BY count DESC
LIMIT 15