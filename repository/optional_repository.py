from sqlalchemy import select
from model.optional import Optional
from model.car_model import model_optional
 
 
# GET ALL
def get_all(session):
    return session.execute(select(Optional)).scalars().all()
 
 
# GET BY ID
def get_by_id(session, optional_id):
    return session.get(Optional, optional_id)
 
 
# GET BY MODEL: restituisce tutti gli optional disponibili per un dato modello
def get_by_model(session, model_id):
    return session.execute(
        select(Optional).join(model_optional).where(model_optional.c.model_id == model_id)
    ).scalars().all()
 
 
# CREATE
def create(session, optional):
    session.add(optional)
    session.commit()
    return optional
 
 
# UPDATE
def update(session, optional):
    session.commit()
    return optional
 
 
# DELETE
def delete_by_id(session, optional):
    session.delete(optional)
    session.commit()