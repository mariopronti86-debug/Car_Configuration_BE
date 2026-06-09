from sqlalchemy import select
from model.configuration import Configuration
 
 
# GET ALL
def get_all(session):
    return session.execute(select(Configuration)).scalars().all()
 
 
# GET BY ID
def get_by_id(session, configuration_id):
    return session.get(Configuration, configuration_id)
 
 
# GET BY CLIENT: recupera tutte le configurazioni di un client
def get_by_client(session, client_id):
    return session.execute(
        select(Configuration).filter_by(client_id=client_id)
    ).scalars().all()
 
 
# CREATE
def create(session, configuration):
    session.add(configuration)
    session.commit()
    return configuration
 
 
# UPDATE
def update(session, configuration):
    session.commit()
    return configuration
 
 
# DELETE
def delete_by_id(session, configuration):
    session.delete(configuration)
    session.commit()