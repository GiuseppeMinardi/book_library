SELECT 
    b.isbn,
    b.title,
    b.language,
    substr(b.publishedDate, 1, 4) as publishedYear,
    b.publisher,
    b.pageCount,
    a.n_authors as nAuthors,
    be.vector as embedding_vector,
    b.description
from books b
join book_embeddings be on b.id = be.book_id
join (select book_id, count(distinct author_id) as n_authors from book_authors group by book_id) a on b.id = a.book_id
where be.model_name = :model_name