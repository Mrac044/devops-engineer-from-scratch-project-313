import db_models

from . import db_engine
from sqlmodel import Field, Session, SQLModel


def create_db_and_tables():
    SQLModel.metadata.create_all(db_engine)


if __name__ == "__main__":
    create_db_and_tables()
