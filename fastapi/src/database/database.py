from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

DATABASE_URL = "postgresql+asyncpg://postgres:Mehemmed200405@localhost:5432/project"

engine = create_engine(
    DATABASE_URL.replace("asyncpg", "psycopg2"),
    echo=True,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
