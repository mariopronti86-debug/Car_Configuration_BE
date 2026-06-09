from sqlalchemy import select
from model.car_model import CarModel
 
 
# GET ALL
def get_all(session):
    return session.execute(select(CarModel)).scalars().all()
 
 
# GET BY ID
def get_by_id(session, model_id):
    return session.get(CarModel, model_id)
 
 
# CREATE
def create(session, car_model):
    session.add(car_model)
    session.commit()
    return car_model
 
 
# UPDATE
def update(session, car_model):
    session.commit()
    return car_model
 
 
# DELETE
def delete_by_id(session, car_model):
    session.delete(car_model)
    session.commit()
