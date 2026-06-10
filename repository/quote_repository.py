from sqlalchemy import select
from model.quote import Quote
from model.configuration import Configuration


# GET ALL
def get_all(session):
    return session.execute(select(Quote)).scalars().all()


# GET BY ID
def get_by_id(session, quote_id):
    return session.get(Quote, quote_id)


# GET BY CLIENT: preventivi del client tramite join con Configuration
def get_by_client(session, client_id):
    return session.execute(
        select(Quote).join(Configuration).filter(Configuration.client_id == client_id)
    ).scalars().all()


# GET LAST: serve per generare il numero progressivo
def get_last(session):
    return session.execute(
        select(Quote).order_by(Quote.quote_id.desc())
    ).scalars().first()


# CREATE
def create(session, quote):
    session.add(quote)
    session.commit()
    return quote


# UPDATE
def update(session, quote):
    session.commit()
    return quote


# DELETE
def delete_by_id(session, quote):
    session.delete(quote)
    session.commit()