from model.configuration import Configuration
from repository import (
    configuration_repository,
    car_model_repository,
    engine_repository,
    optional_repository,
    user_repository,
)
from service import compatibility_service


# ── Calcolo prezzo (metodo privato di supporto) 
def _calcola_prezzo(car_model, engine, optionals):
    totale = float(car_model.base_price) + float(engine.extra_price)
    for opt in optionals:
        totale += float(opt.price)
    return round(totale, 2)


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

    for campo in ["name", "model_id", "engine_id"]:
        if campo not in data:
            raise ValueError(f"Campo '{campo}' obbligatorio!")

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
        # Verifica che l'optional sia disponibile per questo modello
        if opt not in car_model.optionals:
            raise ValueError(f"Optional '{opt.name}' non disponibile per il modello '{car_model.name}'!")
        optionals.append(opt)

    # Controllo regole di compatibilità tra gli optional selezionati
    violazioni = compatibility_service.check_optional_list(session, optional_ids)
    if violazioni:
        msgs = [v["message"] for v in violazioni]
        raise ValueError("Errori di compatibilità: " + " | ".join(msgs))

    total_price = _calcola_prezzo(car_model, engine, optionals)

    nuova_conf = Configuration(
        name=data["name"],
        status="draft",
        total_price=total_price,
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
        raise ValueError("Impossibile modificare una configurazione per cui esiste già un preventivo!")

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
                raise ValueError(f"Optional '{opt.name}' non disponibile per il modello '{conf.car_model.name}'!")
            optionals.append(opt)

        violazioni = compatibility_service.check_optional_list(session, optional_ids)
        if violazioni:
            msgs = [v["message"] for v in violazioni]
            raise ValueError("Errori di compatibilità: " + " | ".join(msgs))

        conf.optionals = optionals

    # Ricalcolo automatico del prezzo dopo ogni modifica
    engine = engine_repository.get_by_id(session, conf.engine_id)
    conf.total_price = _calcola_prezzo(conf.car_model, engine, conf.optionals)

    return configuration_repository.update(session, conf)


# ── DELETE 
def delete(session, configuration_id, client_id, is_admin=False):
    conf = get_by_id(session, configuration_id)

    if not is_admin and conf.client_id != client_id:
        raise ValueError("Non sei autorizzato a eliminare questa configurazione!")

    configuration_repository.delete_by_id(session, conf)