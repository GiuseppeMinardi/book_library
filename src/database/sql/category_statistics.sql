-- Query to get statistics for each category
-- Shows category name, number of books, and average page count

SELECT 
    c.name as category,
    COUNT(b.id) as book_count,
    ROUND(AVG(b.pageCount), 0) as avg_pages,
    MIN(b.publishedDate) as oldest_book_year,
    MAX(b.publishedDate) as newest_book_year
FROM categories c
LEFT JOIN book_categories bc ON c.id = bc.category_id
LEFT JOIN books b ON bc.book_id = b.id
GROUP BY c.id
ORDER BY book_count DESC;
