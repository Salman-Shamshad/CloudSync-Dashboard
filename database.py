import sqlite3
import os

DB_NAME = "cloudsync.db"

def init_db():
    """Initializes the SQLite database with necessary tables."""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Table for storing user sessions or settings (simplified for demo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for caching file metadata to reduce API calls
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_cache (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mime_type TEXT,
                size INTEGER,
                last_modified TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database {DB_NAME} initialized.")
    else:
        print(f"Database {DB_NAME} already exists.")

def get_db_connection():
    """Returns a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
