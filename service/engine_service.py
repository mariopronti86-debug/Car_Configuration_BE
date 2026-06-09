from model.engine import Engine
from repository import engine_repository
 
 
# ── GET ALL
def get_all(session):
    return engine_repository.get_all(session)
 
 
# ── GET BY ID 
def get_by_id(session, engine_id):
    engine = engine_repository.get_by_id(session, engine_id)
 
    if engine is None:
        raise ValueError(f"Engine con id={engine_id} non trovato!")
 
    return engine
 
 
# ── CREATE 
def create(session, data):
 
    for campo in ["fuel_type", "power_hp", "extra_price"]:
        if campo not in data:
            raise ValueError(f"Campo '{campo}' obbligatorio!")
 
    if int(data["power_hp"]) <= 0:
        raise ValueError("La potenza deve essere maggiore di 0!")
 
    if float(data["extra_price"]) < 0:
        raise ValueError("Il prezzo extra non può essere negativo!")
 
    nuovo_engine = Engine(
        fuel_type=data["fuel_type"],
        power_hp=int(data["power_hp"]),
        extra_price=float(data["extra_price"]),
    )
 
    return engine_repository.create(session, nuovo_engine)
 
 
# ── UPDATE 
def update(session, engine_id, data):
    engine = get_by_id(session, engine_id)
 
    if "fuel_type" in data:
        engine.fuel_type = data["fuel_type"]
 
    if "power_hp" in data:
        if int(data["power_hp"]) <= 0:
            raise ValueError("La potenza deve essere maggiore di 0!")
        engine.power_hp = int(data["power_hp"])
 
    if "extra_price" in data:
        if float(data["extra_price"]) < 0:
            raise ValueError("Il prezzo extra non può essere negativo!")
        engine.extra_price = float(data["extra_price"])
 
    return engine_repository.update(session, engine)
 
 
# ── DELETE 
def delete(session, engine_id):
    engine = get_by_id(session, engine_id)
    engine_repository.delete_by_id(session, engine)