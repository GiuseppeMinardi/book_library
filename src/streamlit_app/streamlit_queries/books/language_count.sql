SELECT 
    b.language,
    COUNT(distinct b.isbn) as book_count
FROM books b
GROUP BY b.language
ORDER BY book_count DESC