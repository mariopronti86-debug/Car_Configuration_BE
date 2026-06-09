from model.car_model import CarModel
from repository import car_model_repository, engine_repository, optional_repository
 
 
# ── GET ALL 
def get_all(session):
    return car_model_repository.get_all(session)
 
 
# ── GET BY ID 
def get_by_id(session, model_id):
    car_model = car_model_repository.get_by_id(session, model_id)
 
    if car_model is None:
        raise ValueError(f"Modello con id={model_id} non trovato!")
 
    return car_model
 
 
# ── CREATE 
def create(session, data):
 
    for campo in ["name", "brand", "base_price", "engine_id"]:
        if campo not in data:
            raise ValueError(f"Campo '{campo}' obbligatorio!")
 
    if float(data["base_price"]) < 0:
        raise ValueError("Il prezzo base non può essere negativo!")
 
    # Verifica che l'engine esista prima di collegarlo
    engine = engine_repository.get_by_id(session, int(data["engine_id"]))
    if engine is None:
        raise ValueError(f"Engine con id={data['engine_id']} non trovato!")
 
    nuovo_modello = CarModel(
        name=data["name"],
        brand=data["brand"],
        base_price=float(data["base_price"]),
        category=data.get("category"),
        engine_id=int(data["engine_id"]),
    )
 
    return car_model_repository.create(session, nuovo_modello)
 
 
# ── UPDATE 
def update(session, model_id, data):
    car_model = get_by_id(session, model_id)
 
    if "name" in data:
        car_model.name = data["name"]
 
    if "brand" in data:
        car_model.brand = data["brand"]
 
    if "base_price" in data:
        if float(data["base_price"]) < 0:
            raise ValueError("Il prezzo base non può essere negativo!")
        car_model.base_price = float(data["base_price"])
 
    if "category" in data:
        car_model.category = data["category"]
 
    if "engine_id" in data:
        engine = engine_repository.get_by_id(session, int(data["engine_id"]))
        if engine is None:
            raise ValueError(f"Engine con id={data['engine_id']} non trovato!")
        car_model.engine_id = int(data["engine_id"])
 
    return car_model_repository.update(session, car_model)
 
 
# ── DELETE 
def delete(session, model_id):
    car_model = get_by_id(session, model_id)
    car_model_repository.delete_by_id(session, car_model)
 
 
# ── ADD OPTIONAL al catalogo del modello 
def add_optional(session, model_id, optional_id):
    car_model = get_by_id(session, model_id)
    optional  = optional_repository.get_by_id(session, optional_id)
 
    if optional is None:
        raise ValueError(f"Optional con id={optional_id} non trovato!")
 
    if optional in car_model.optionals:
        raise ValueError("Optional già associato a questo modello!")
 
    car_model.optionals.append(optional)
    session.commit()
 
    return car_model
 
 
# ── REMOVE OPTIONAL dal catalogo del modello 
def remove_optional(session, model_id, optional_id):
    car_model = get_by_id(session, model_id)
    optional  = optional_repository.get_by_id(session, optional_id)
 
    if optional is None:
        raise ValueError(f"Optional con id={optional_id} non trovato!")
 
    if optional not in car_model.optionals:
        raise ValueError("Optional non associato a questo modello!")
 
    car_model.optionals.remove(optional)
    session.commit()
 
    return car_model