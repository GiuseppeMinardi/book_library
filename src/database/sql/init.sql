-- ENABLE THE EXTENSION FIRST
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Create the base tables first

CREATE TABLE books (
    id TEXT PRIMARY KEY,
    title TEXT,
    publisher TEXT,
    publishedDate TEXT,
    description TEXT,
    pageCount INTEGER,
    printType TEXT,
    language TEXT,
    infoLink TEXT,
    smallThumbnail TEXT,
    isbn TEXT UNIQUE
);

CREATE TABLE authors (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE,
    birth_date TEXT,
    death_date TEXT,
    nationality TEXT,
    sex TEXT,
    bio TEXT,
    author_link TEXT
);

CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE
);

-- 2. Create the relationship (join) tables

CREATE TABLE book_authors (
    book_id TEXT REFERENCES books(id) ON DELETE CASCADE,
    author_id TEXT REFERENCES authors(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE book_categories (
    book_id TEXT REFERENCES books(id) ON DELETE CASCADE,
    category_id TEXT REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, category_id)
);

-- 3. Create the embeddings tables
-- UPDATE THE EMBEDDING TABLES
CREATE TABLE book_embeddings (
    book_id TEXT REFERENCES books(id) ON DELETE CASCADE,
    model_name TEXT,
    -- Change BYTEA to VECTOR with your specific dimensions
    vector VECTOR(1536), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, model_name)
);

CREATE TABLE author_embeddings (
    author_id TEXT REFERENCES authors(id) ON DELETE CASCADE,
    model_name TEXT,
    -- Change BYTEA to VECTOR
    vector VECTOR(1536), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (author_id, model_name)
);