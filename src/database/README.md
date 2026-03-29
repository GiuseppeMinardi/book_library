# DATABASE

```mermaid
erDiagram

    books {
        TEXT id PK
        TEXT title
        TEXT publisher
        TEXT publishedDate
        TEXT description
        INTEGER pageCount
        TEXT printType
        TEXT language
        TEXT infoLink
        TEXT smallThumbnail
        TEXT isbn UNIQUE
    }

    authors {
        TEXT id PK
        TEXT name UNIQUE
        TEXT birth_date
        TEXT death_date
        TEXT nationality
        TEXT sex
        TEXT bio
        TEXT author_link
    }

    categories {
        TEXT id PK
        TEXT name UNIQUE
    }

    book_authors {
        TEXT book_id PK
        TEXT author_id PK
    }

    book_categories {
        TEXT book_id PK
        TEXT category_id PK
    }

    book_embeddings {
        TEXT book_id PK
        TEXT model_name PK
        BLOB vector
        TIMESTAMP created_at
    }

    author_embeddings {
        TEXT author_id PK
        TEXT model_name PK
        BLOB vector
        TIMESTAMP created_at
    }

    books ||--o{ book_authors : "has"
    authors ||--o{ book_authors : "has"
    books ||--o{ book_categories : "has"
    categories ||--o{ book_categories : "has"
    books ||--o{ book_embeddings : "has"
    authors ||--o{ author_embeddings : "has"
```
