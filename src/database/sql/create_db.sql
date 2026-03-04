CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    publishedDate TEXT,
    description TEXT,
    pageCount INTEGER,
    printType TEXT,
    language TEXT,
    infoLink TEXT,
    smallThumbnail TEXT,
    isbn TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS authors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birth_date TEXT,
    death_date TEXT,
    nationality TEXT,
    sex TEXT,
    bio TEXT,
    author_link TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id TEXT,
    author_id TEXT,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS book_categories (
    book_id TEXT,
    category_id TEXT,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS book_embeddings (
    book_id TEXT,
    model_name TEXT,
    vector BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, model_name),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS author_embeddings (
    author_id TEXT,
    model_name TEXT,
    vector BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (author_id, model_name),
    FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE
);