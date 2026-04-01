-- ==========================================
-- 1. CATEGORIES
-- ==========================================
INSERT INTO categories (name) VALUES 
('Fiction'), 
('Science'), 
('History'),
('Fantasy'), 
('Biography'), 
('Physics');

-- ==========================================
-- 2. AUTHORS
-- ==========================================
INSERT INTO authors (name, birth_date, nationality, sex, bio) VALUES 
('J.R.R. Tolkien', '1892-01-03', 'British', 'M', 'Author of Middle-earth.'),
('Stephen Hawking', '1942-01-08', 'British', 'M', 'Theoretical physicist and cosmologist.'),
('Ursula K. Le Guin', '1929-10-21', 'American', 'F', 'Award-winning author of speculative fiction.'),
('Walter Isaacson', '1952-05-20', 'American', 'M', 'Historian and biographer.');

-- ==========================================
-- 3. BOOKS
-- ==========================================
INSERT INTO books (title, publisher, published_date, isbn) VALUES 
('The Hobbit', 'George Allen & Unwin', '1937-09-21', '9780007525492'),
('A Brief History of Time', 'Bantam Books', '1988-04-01', '9780553380163'),
('A Wizard of Earthsea', 'Parnassus', '1968-11-01', '9780547773742'),
('Steve Jobs', 'Simon & Schuster', '2011-10-24', '9781451648539'),
('The Grand Design', 'Bantam Books', '2010-09-07', '9780553805376');

-- ==========================================
-- 4. RELATIONSHIPS (JOIN TABLES)
-- ==========================================

-- Book-to-Author Mapping
INSERT INTO book_authors (book_id, author_id) VALUES 
((SELECT id FROM books WHERE title = 'The Hobbit'), (SELECT id FROM authors WHERE name = 'J.R.R. Tolkien')),
((SELECT id FROM books WHERE title = 'A Brief History of Time'), (SELECT id FROM authors WHERE name = 'Stephen Hawking')),
((SELECT id FROM books WHERE title = 'A Wizard of Earthsea'), (SELECT id FROM authors WHERE name = 'Ursula K. Le Guin')),
((SELECT id FROM books WHERE title = 'Steve Jobs'), (SELECT id FROM authors WHERE name = 'Walter Isaacson')),
((SELECT id FROM books WHERE title = 'The Grand Design'), (SELECT id FROM authors WHERE name = 'Stephen Hawking'));

-- Book-to-Category Mapping
INSERT INTO book_categories (book_id, category_id) VALUES 
((SELECT id FROM books WHERE title = 'The Hobbit'), (SELECT id FROM categories WHERE name = 'Fiction')),
((SELECT id FROM books WHERE title = 'The Hobbit'), (SELECT id FROM categories WHERE name = 'Fantasy')),
((SELECT id FROM books WHERE title = 'A Brief History of Time'), (SELECT id FROM categories WHERE name = 'Science')),
((SELECT id FROM books WHERE title = 'A Brief History of Time'), (SELECT id FROM categories WHERE name = 'Physics')),
((SELECT id FROM books WHERE title = 'A Wizard of Earthsea'), (SELECT id FROM categories WHERE name = 'Fantasy')),
((SELECT id FROM books WHERE title = 'Steve Jobs'), (SELECT id FROM categories WHERE name = 'Biography')),
((SELECT id FROM books WHERE title = 'The Grand Design'), (SELECT id FROM categories WHERE name = 'Science')),
((SELECT id FROM books WHERE title = 'The Grand Design'), (SELECT id FROM categories WHERE name = 'Physics'));

-- ==========================================
-- 5. VECTOR EMBEDDINGS (pgvector)
-- ==========================================
-- Using slightly different values to test similarity searches
INSERT INTO book_embeddings (book_id, model_name, vector) VALUES 
(
    (SELECT id FROM books WHERE title = 'The Hobbit'), 
    'text-embedding-3-small', 
    array_fill(0.1::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM books WHERE title = 'A Brief History of Time'), 
    'text-embedding-3-small', 
    array_fill(0.8::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM books WHERE title = 'A Wizard of Earthsea'), 
    'text-embedding-3-small', 
    array_fill(0.12::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM books WHERE title = 'The Grand Design'), 
    'text-embedding-3-small', 
    array_fill(0.85::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM books WHERE title = 'Steve Jobs'), 
    'text-embedding-3-small', 
    array_fill(0.44::float, ARRAY[1536])::vector
);

-- ==========================================
-- 6. AUTHOR VECTOR EMBEDDINGS (pgvector)
-- ==========================================
INSERT INTO author_embeddings (author_id, model_name, vector) VALUES 
(
    (SELECT id FROM authors WHERE name = 'J.R.R. Tolkien'), 
    'text-embedding-3-small', 
    array_fill(0.11::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM authors WHERE name = 'Stephen Hawking'), 
    'text-embedding-3-small', 
    array_fill(0.81::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM authors WHERE name = 'Ursula K. Le Guin'), 
    'text-embedding-3-small', 
    array_fill(0.13::float, ARRAY[1536])::vector
),
(
    (SELECT id FROM authors WHERE name = 'Walter Isaacson'), 
    'text-embedding-3-small', 
    array_fill(0.45::float, ARRAY[1536])::vector
);