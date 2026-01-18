
import streamlit as st

from src.database.db import Database

# Page config
st.set_page_config(page_title="📚 Book Library", layout="wide")

# Initialize database
@st.cache_resource
def get_database():
    return Database()

db = get_database()

# Sidebar navigation
st.sidebar.title("📚 Book Library")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "📖 Books", "✍️ Authors", "🏷️ Categories"]
)

# Main content
if page == "📊 Overview":
    st.title("Library Overview")
    
    with db:
        # Get summary statistics
        summary = db.run_query("""
            SELECT 
                (SELECT COUNT(*) FROM books) as total_books,
                (SELECT COUNT(*) FROM authors) as total_authors,
                (SELECT COUNT(*) FROM categories) as total_categories,
                (SELECT ROUND(AVG(pageCount), 0) FROM books WHERE pageCount IS NOT NULL) as avg_pages,
                (SELECT MAX(pageCount) FROM books WHERE pageCount IS NOT NULL) as max_pages
        """, as_dataframe=False)
        
        if summary:
            stats = summary[0]
            
            # Display metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("📖 Total Books", stats["total_books"])
            with col2:
                st.metric("✍️ Authors", stats["total_authors"])
            with col3:
                st.metric("🏷️ Categories", stats["total_categories"])
            with col4:
                st.metric("📄 Avg Pages", int(stats["avg_pages"]) if stats["avg_pages"] else 0)
            with col5:
                st.metric("📏 Max Pages", stats["max_pages"] if stats["max_pages"] else 0)
        
        st.divider()
        
        # Most prolific authors
        st.subheader("Top 10 Most Prolific Authors")
        authors_df = db.run_query("""
            SELECT 
                a.name,
                COUNT(ba.book_id) as book_count
            FROM authors a
            LEFT JOIN book_authors ba ON a.id = ba.author_id
            GROUP BY a.id
            ORDER BY book_count DESC
            LIMIT 10
        """, as_dataframe=True)
        
        if authors_df is not None and not authors_df.empty:
            st.bar_chart(authors_df.set_index("name")["book_count"])
            st.dataframe(authors_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Books by category
        st.subheader("Books by Category")
        category_df = db.run_query("""
            SELECT 
                c.name,
                COUNT(bc.book_id) as count
            FROM categories c
            LEFT JOIN book_categories bc ON c.id = bc.category_id
            GROUP BY c.id
            ORDER BY count DESC
            LIMIT 15
        """, as_dataframe=True)
        
        if category_df is not None and not category_df.empty:
            st.bar_chart(category_df.set_index("name")["count"])

elif page == "📖 Books":
    st.title("📖 Books")
    
    with db:
        # Search and filters
        col1, col2 = st.columns(2)
        
        with col1:
            search_title = st.text_input("Search by title", placeholder="e.g., The Hobbit")
        
        with col2:
            language_filter = st.selectbox(
                "Filter by language",
                ["All"] + db.run_query(
                    "SELECT DISTINCT language FROM books WHERE language IS NOT NULL ORDER BY language",
                    as_dataframe=False
                )[0] if db.run_query(
                    "SELECT DISTINCT language FROM books WHERE language IS NOT NULL ORDER BY language",
                    as_dataframe=False
                ) else ["All"]
            )
        
        # Build query
        query = """
            SELECT 
                b.title,
                b.publisher,
                b.publishedDate,
                b.pageCount,
                b.language,
                b.isbn
            FROM books b
            WHERE 1=1
        """
        params = []
        
        if search_title:
            query += " AND b.title LIKE ?"
            params.append(f"%{search_title}%")
        
        if language_filter != "All":
            query += " AND b.language = ?"
            params.append(language_filter)
        
        query += " ORDER BY b.title LIMIT 100"
        
        # Get books
        books_df = db.run_query(query, tuple(params), as_dataframe=True)
        
        st.subheader(f"Books ({len(books_df) if books_df is not None else 0})")
        
        if books_df is not None and not books_df.empty:
            st.dataframe(books_df, use_container_width=True, hide_index=True)
        else:
            st.info("No books found matching your criteria.")

elif page == "✍️ Authors":
    st.title("✍️ Authors")
    
    with db:
        # Search
        search_author = st.text_input("Search by author name", placeholder="e.g., J.R.R. Tolkien")
        
        # Build query
        query = """
            SELECT 
                a.name,
                a.nationality,
                a.birth_date,
                a.death_date,
                COUNT(ba.book_id) as books
            FROM authors a
            LEFT JOIN book_authors ba ON a.id = ba.author_id
            WHERE 1=1
        """
        params = []
        
        if search_author:
            query += " AND a.name LIKE ?"
            params.append(f"%{search_author}%")
        
        query += " GROUP BY a.id ORDER BY books DESC LIMIT 100"
        
        # Get authors
        authors_df = db.run_query(query, tuple(params), as_dataframe=True)
        
        st.subheader(f"Authors ({len(authors_df) if authors_df is not None else 0})")
        
        if authors_df is not None and not authors_df.empty:
            st.dataframe(authors_df, use_container_width=True, hide_index=True)
        else:
            st.info("No authors found matching your criteria.")

elif page == "🏷️ Categories":
    st.title("🏷️ Categories")
    
    with db:
        # Get categories with book counts
        categories_df = db.run_query("""
            SELECT 
                c.name,
                COUNT(bc.book_id) as book_count
            FROM categories c
            LEFT JOIN book_categories bc ON c.id = bc.category_id
            GROUP BY c.id
            ORDER BY book_count DESC
        """, as_dataframe=True)
        
        if categories_df is not None and not categories_df.empty:
            # Show chart
            st.subheader(f"Categories ({len(categories_df)})")
            st.bar_chart(categories_df.set_index("name")["book_count"])
            
            # Show table
            st.dataframe(categories_df, use_container_width=True, hide_index=True)
        else:
            st.info("No categories found.")

st.sidebar.divider()
st.sidebar.info("📚 Book Library Dashboard - Powered by Streamlit")
