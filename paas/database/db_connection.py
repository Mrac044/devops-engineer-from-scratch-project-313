import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")

db_engine = create_engine(database_url, echo=True)

def get_session():
    with Session(db_engine) as session:
        yield session