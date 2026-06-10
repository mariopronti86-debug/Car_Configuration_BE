from sqlalchemy import select
from model.engine import Engine


# GET ALL
def get_all(session):
    return session.execute(select(Engine)).scalars().all()


# GET BY ID
def get_by_id(session, engine_id):
    return session.get(Engine, engine_id)


# CREATE
def create(session, engine):
    session.add(engine)
    session.commit()
    return engine


# UPDATE
def update(session, engine):
    session.commit()
    return engine


# DELETE
def delete_by_id(session, engine):
    session.delete(engine)
    session.commit()