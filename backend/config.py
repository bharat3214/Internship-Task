import os
from pymongo import MongoClient
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def _require_env(name: str) -> str:
    """Fetch required env var or raise a clear error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

# MongoDB Configuration
MONGO_URI = _require_env('MONGO_URI')
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client['todo_app']
users_collection = mongo_db['users']
todos_mongo_collection = mongo_db['todos']

# PostgreSQL Configuration
POSTGRES_URI = _require_env('POSTGRES_URI')

def get_postgres_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(POSTGRES_URI)

def init_postgres_table():
    """Initialize PostgreSQL todos table"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            task TEXT NOT NULL,
            description TEXT,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Add description column if it doesn't exist (for existing tables)
    cursor.execute('''
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='todos' AND column_name='description') THEN
                ALTER TABLE todos ADD COLUMN description TEXT;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='todos' AND column_name='priority') THEN
                ALTER TABLE todos ADD COLUMN priority VARCHAR(10) DEFAULT 'LOW';
            END IF;
        END $$;
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# JWT Configuration
JWT_SECRET_KEY = _require_env('JWT_SECRET_KEY')
