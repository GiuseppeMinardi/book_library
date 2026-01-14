-- Query to show books publication timeline
-- Groups by publication year with book count

SELECT 
    SUBSTR(publishedDate, 1, 4) as publication_year,
    COUNT(*) as book_count,
    ROUND(AVG(pageCount), 0) as avg_pages
FROM books
WHERE publishedDate IS NOT NULL
GROUP BY publication_year
ORDER BY publication_year DESC;
