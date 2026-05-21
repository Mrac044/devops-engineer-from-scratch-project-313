import sys

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

app_file_module = sys.modules['paas.scripts.app']

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

app_file_module.db_engine = test_engine


@pytest.fixture(name="session", autouse=True)
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture():
    flask_app = app_file_module.app
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client
