from sqlmodel import Session, func, select

from .. import database


def get_links_by_created_at():
    with Session(database.db_engine) as session:
            links = session.exec(
                select(database.db_models.Links)
                .order_by(database.db_models.Links.created_at)
                ).all()
    return links


def get_links_with_pagination(start, limit_count):
    with Session(database.db_engine) as session:
        total_links = session.exec(
            select(func.count(database.db_models.Links.id))
            ).one()
        links = session.exec(
            select(database.db_models.Links)
            .order_by(database.db_models.Links.created_at)
            .offset(start)
            .limit(limit_count)
            ).all()
    return links, total_links


def get_short_name_if_exists(short_name):
    with Session(database.db_engine) as session:
        short_name = session.exec(select(database.db_models.Links)
            .where(database.db_models.Links.short_name == short_name)
        ).first()
    return short_name


def get_link_by_id(id):
    with Session(database.db_engine) as session:
        link = session.exec(select(database.db_models.Links)
            .where(database.db_models.Links.id == id)
            ).first()
        return link


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
