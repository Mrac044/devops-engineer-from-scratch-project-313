import os

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

load_dotenv()

database_url = os.getenv("DATABASE_URL") or 'sqlite:///:memory:'
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
db_engine = create_engine(database_url, echo=True)

def get_session():
    with Session(db_engine) as session:
        yield session
