-- Query to get statistics on books by language
-- Shows language, number of books, and average page count

SELECT 
    language,
    COUNT(*) as book_count,
    ROUND(AVG(pageCount), 0) as avg_pages,
    MIN(pageCount) as min_pages,
    MAX(pageCount) as max_pages
FROM books
WHERE language IS NOT NULL
GROUP BY language
ORDER BY book_count DESC;
