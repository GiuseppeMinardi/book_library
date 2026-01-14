-- Query to get a comprehensive summary of the library
-- Shows overall statistics

SELECT 
    (SELECT COUNT(*) FROM books) as total_books,
    (SELECT COUNT(*) FROM authors) as total_authors,
    (SELECT COUNT(*) FROM categories) as total_categories,
    (SELECT COUNT(*) FROM books WHERE language IS NOT NULL) as books_with_language,
    (SELECT COUNT(*) FROM books WHERE pageCount IS NOT NULL) as books_with_page_count,
    (SELECT ROUND(AVG(pageCount), 0) FROM books) as avg_page_count,
    (SELECT MIN(publishedDate) FROM books) as oldest_publication,
    (SELECT MAX(publishedDate) FROM books) as newest_publication;
