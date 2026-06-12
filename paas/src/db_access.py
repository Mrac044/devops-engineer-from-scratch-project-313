from sqlmodel import Session

from .. import database


def db_request(statement, fetch_all=False):
    with Session(database.db_engine) as session:
        result = session.exec(statement)
        if fetch_all:
            return result.all()
        return result.first()


def db_write(action, model_object):
    with Session(database.db_engine) as session:
        if action == 'delete':
            session.delete(model_object)
        else:
            session.add(model_object)
        session.commit()
        if action != 'delete':
            session.refresh(model_object)
        return model_object
