select 
    a.id,
    a.name,
    a.birth_date,
    a.death_date,
    a.nationality,
    a.sex,
    ae.vector as embedding_vector,
    ba.n_books,
    a.bio
from authors a
left join (
select 
    author_id, 
    count(distinct book_id) as n_books from book_authors
group by author_id
)  ba on a.id = ba.author_id
join author_embeddings ae on a.id = ae.author_id
where ae.model_name = :model_name


