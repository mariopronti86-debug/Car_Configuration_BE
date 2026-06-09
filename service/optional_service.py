from model.optional import Optional
from repository import optional_repository


# ── GET ALL 
def get_all(session):
    return optional_repository.get_all(session)


# ── GET BY ID 
def get_by_id(session, optional_id):
    optional = optional_repository.get_by_id(session, optional_id)

    if optional is None:
        raise ValueError(f"Optional con id={optional_id} non trovato!")

    return optional


# ── GET BY MODEL 
def get_by_model(session, model_id):
    return optional_repository.get_by_model(session, model_id)


# ── CREATE 
def create(session, data):

    for campo in ["name", "price"]:
        if campo not in data:
            raise ValueError(f"Campo '{campo}' obbligatorio!")

    if float(data["price"]) < 0:
        raise ValueError("Il prezzo non può essere negativo!")

    nuovo_optional = Optional(
        name=data["name"],
        category=data.get("category"),
        price=float(data["price"]),
    )

    return optional_repository.create(session, nuovo_optional)


# ── UPDATE 
def update(session, optional_id, data):
    optional = get_by_id(session, optional_id)

    if "name" in data:
        optional.name = data["name"]

    if "category" in data:
        optional.category = data["category"]

    if "price" in data:
        if float(data["price"]) < 0:
            raise ValueError("Il prezzo non può essere negativo!")
        optional.price = float(data["price"])

    return optional_repository.update(session, optional)


# ── DELETE 
def delete(session, optional_id):
    optional = get_by_id(session, optional_id)
    optional_repository.delete_by_id(session, optional)