# app/db/database.py

from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

# Ensure the URL uses the correct driver
connection_string = settings.DATABASE_URL
if "postgresql" in connection_string and "+psycopg" not in connection_string:
    connection_string = connection_string.replace("postgresql", "postgresql+psycopg")

# Prevent double replacement if already done
connection_string = connection_string.replace("+psycopg+psycopg", "+psycopg")

# Database engine configuration
engine = create_engine(
    connection_string,
    connect_args={"sslmode": "require"},  # Required for Neon
    pool_recycle=300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
