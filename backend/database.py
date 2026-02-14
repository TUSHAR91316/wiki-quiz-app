from sqlmodel import SQLModel, create_engine, Session, text
import os
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wiki_quiz.db")

def create_database_if_not_exists(url):
    """
    Checks if the database exists and creates it if not.
    Only works for PostgreSQL.
    """
    try:
        db_url = make_url(url)
        if 'postgresql' in db_url.drivername:
            # Connect to default 'postgres' db to create the target db
            default_url = db_url._replace(database='postgres')
            engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
            
            with engine.connect() as conn:
                db_name = db_url.database
                # Check if db exists
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
                if not result.scalar():
                    print(f"Database {db_name} does not exist. Creating...")
                    conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                    print(f"Database {db_name} created successfully.")
                else:
                    print(f"Database {db_name} already exists.")
            engine.dispose()
    except Exception as e:
        print(f"Warning: Could not check/create database: {e}")

# Attempt to create DB before creating the main engine
create_database_if_not_exists(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
