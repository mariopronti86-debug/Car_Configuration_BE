from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker




class Base(DeclarativeBase):
    pass


# Per didattica credenziali committate e pushate
engine = create_engine("postgresql://postgres:111111@localhost/car_config", echo=True)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    import model.user          
    import model.engine        
    import model.car_model     
    import model.optional      
    import model.compatibility 
    import model.configuration 
    import model.quote         

    print("[LOG] Inizializzazione database...")
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()