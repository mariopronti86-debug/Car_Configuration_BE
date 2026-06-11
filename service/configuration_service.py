from model.configuration import Configuration
from repository import (
    configuration_repository,
    car_model_repository,
    engine_repository,
    optional_repository,
    user_repository,
)
from service import compatibility_service
 
 
# ── GET ALL
def get_all(session):
    return configuration_repository.get_all(session)
 
 
# ── GET BY ID
def get_by_id(session, configuration_id):
    conf = configuration_repository.get_by_id(session, configuration_id)
 
    if conf is None:
        raise ValueError(f"Configurazione con id={configuration_id} non trovata!")
 
    return conf
 
 
# ── GET BY CLIENT
def get_by_client(session, client_id):
    return configuration_repository.get_by_client(session, client_id)
 
 
# ── CREATE
def create(session, data, client_id):
 
    if not data.get("name") or not data.get("model_id") or not data.get("engine_id"):
        raise ValueError("name, model_id e engine_id sono obbligatori!")
 
    client = user_repository.get_client_by_id(session, client_id)
    if client is None:
        raise ValueError("Client non trovato!")
 
    car_model = car_model_repository.get_by_id(session, int(data["model_id"]))
    if car_model is None:
        raise ValueError(f"Modello con id={data['model_id']} non trovato!")
 
    engine = engine_repository.get_by_id(session, int(data["engine_id"]))
    if engine is None:
        raise ValueError(f"Engine con id={data['engine_id']} non trovato!")
 
    optional_ids = [int(x) for x in data.get("optional_ids", [])]
    optionals = []
 
    for opt_id in optional_ids:
        opt = optional_repository.get_by_id(session, opt_id)
        if opt is None:
            raise ValueError(f"Optional con id={opt_id} non trovato!")
        if opt not in car_model.optionals:
            raise ValueError(f"Optional '{opt.name}' non disponibile per questo modello!")
        optionals.append(opt)
 
    violazioni = compatibility_service.check_optional_list(session, optional_ids)
    if violazioni:
        raise ValueError("Errori compatibilità: " + " | ".join(violazioni))
 
    total_price = float(car_model.base_price) + float(engine.extra_price)
    for opt in optionals:
        total_price += float(opt.price)
 
    nuova_conf = Configuration(
        name=data["name"],
        status="draft",
        total_price=round(total_price, 2),
        client_id=client_id,
        model_id=car_model.model_id,
        engine_id=engine.engine_id,
    )
    nuova_conf.optionals = optionals
 
    return configuration_repository.create(session, nuova_conf)
 
 
# ── UPDATE
def update(session, configuration_id, data, client_id, is_admin=False):
    conf = get_by_id(session, configuration_id)
 
    if not is_admin and conf.client_id != client_id:
        raise ValueError("Non sei autorizzato a modificare questa configurazione!")
 
    if conf.status == "quoted":
        raise ValueError("Non puoi modificare una configurazione con preventivo già generato!")
 
    if "name" in data:
        conf.name = data["name"]
 
    if "engine_id" in data:
        engine = engine_repository.get_by_id(session, int(data["engine_id"]))
        if engine is None:
            raise ValueError(f"Engine con id={data['engine_id']} non trovato!")
        conf.engine_id = engine.engine_id
 
    if "optional_ids" in data:
        optional_ids = [int(x) for x in data["optional_ids"]]
        optionals = []
 
        for opt_id in optional_ids:
            opt = optional_repository.get_by_id(session, opt_id)
            if opt is None:
                raise ValueError(f"Optional con id={opt_id} non trovato!")
            if opt not in conf.car_model.optionals:
                raise ValueError(f"Optional '{opt.name}' non disponibile per questo modello!")
            optionals.append(opt)
 
        violazioni = compatibility_service.check_optional_list(session, optional_ids)
        if violazioni:
            raise ValueError("Errori compatibilità: " + " | ".join(violazioni))
 
        conf.optionals = optionals
 
    # Ricalcolo prezzo aggiornato
    engine = engine_repository.get_by_id(session, conf.engine_id)
    total_price = float(conf.car_model.base_price) + float(engine.extra_price)
    for opt in conf.optionals:
        total_price += float(opt.price)
    conf.total_price = round(total_price, 2)
 
    return configuration_repository.update(session, conf)
 
 
# ── DELETE
def delete(session, configuration_id, client_id, is_admin=False):
    conf = get_by_id(session, configuration_id)
 
    if not is_admin and conf.client_id != client_id:
        raise ValueError("Non sei autorizzato a eliminare questa configurazione!")
 
    configuration_repository.delete_by_id(session, conf)