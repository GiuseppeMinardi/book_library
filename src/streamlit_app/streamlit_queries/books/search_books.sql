SELECT 
    b.isbn,
    b.title,
    b.language,
    substr(b.publishedDate, 1, 4) as publishedYear,
    b.publisher,
    b.pageCount,
    b.description
from books b;

select * from authors;
