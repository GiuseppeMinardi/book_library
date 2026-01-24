with book_count as (
select 
    author_id, 
    count(distinct book_id) as n_books from book_authors
group by author_id
)
select 
    a.name,
    a.birth_date,
    a.death_date,
    a.nationality,
    a.sex,
    b.n_books,
    a.bio
from authors a 
join book_count b on a.id = b.author_id