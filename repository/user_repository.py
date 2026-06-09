from sqlalchemy import select
from model.user import User, Client, Admin
 
 
# GET ALL CLIENTS
def get_all_clients(session):
    return session.execute(select(Client)).scalars().all()
 
 
# GET ALL ADMINS
def get_all_admins(session):
    return session.execute(select(Admin)).scalars().all()
 
 
# GET BY ID
def get_by_id(session, user_id):
    return session.get(User, user_id)
 
 
# GET CLIENT BY ID
def get_client_by_id(session, client_id):
    return session.get(Client, client_id)
 
 
# GET BY EMAIL
def get_by_email(session, email):
    return session.execute(select(User).filter_by(email=email)).scalars().first()
 
 
# CREATE
def create(session, user):
    session.add(user)
    session.commit()
    return user
 
 
# UPDATE
def update(session, user):
    session.commit()
    return user
 
 
# DELETE
def delete_by_id(session, user):
    session.delete(user)
    session.commit()
