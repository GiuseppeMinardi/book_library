SELECT 
    (SELECT COUNT(*) FROM books) as total_books,
    (SELECT COUNT(*) FROM authors) as total_authors,
    (SELECT COUNT(*) FROM categories) as total_categories,
    (SELECT ROUND(AVG(pageCount), 0) FROM books WHERE pageCount IS NOT NULL) as avg_pages,
    (SELECT MAX(pageCount) FROM books WHERE pageCount IS NOT NULL) as max_pages