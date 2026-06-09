import datetime

from model.quote import Quote
from repository import quote_repository, configuration_repository


# ── Generazione numero preventivo progressivo (metodo privato) 
def _genera_numero_preventivo(session):
    anno   = datetime.datetime.now().year
    ultimo = quote_repository.get_last(session)

    if ultimo is None:
        progressivo = 1
    else:
        # Estrae il numero progressivo dall'ultimo quote_number (es. "QT-2025-0003" --> 3)
        try:
            progressivo = int(ultimo.quote_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            progressivo = 1

    return f"QT-{anno}-{progressivo:04d}"


# ── GET ALL 
def get_all(session):
    return quote_repository.get_all(session)


# ── GET BY ID 
def get_by_id(session, quote_id):
    quote = quote_repository.get_by_id(session, quote_id)

    if quote is None:
        raise ValueError(f"Preventivo con id={quote_id} non trovato!")

    return quote


# ── GET BY CLIENT 
def get_by_client(session, client_id):
    return quote_repository.get_by_client(session, client_id)


# ── GENERA PREVENTIVO da una configurazione 
def genera_preventivo(session, configuration_id, client_id, data=None, is_admin=False):

    if data is None:
        data = {}

    conf = configuration_repository.get_by_id(session, configuration_id)
    if conf is None:
        raise ValueError(f"Configurazione con id={configuration_id} non trovata!")

    if not is_admin and conf.client_id != client_id:
        raise ValueError("Non sei autorizzato a generare un preventivo per questa configurazione!")

    if conf.status == "quoted":
        raise ValueError("Esiste già un preventivo per questa configurazione!")

    discount_pct = float(data.get("discount_pct", 0))
    if discount_pct < 0 or discount_pct > 100:
        raise ValueError("Lo sconto deve essere compreso tra 0 e 100!")

    # Calcola il prezzo finale applicando lo sconto
    prezzo_base = float(conf.total_price)
    final_price = round(prezzo_base * (1 - discount_pct / 100), 2)

    quote_number = _genera_numero_preventivo(session)

    nuovo_quote = Quote(
        quote_number=quote_number,
        status="pending",
        final_price=final_price,
        discount_pct=discount_pct,
        configuration_id=configuration_id,
    )

    # Aggiorna lo stato della configurazione: non più modificabile
    conf.status = "quoted"
    session.commit()

    return quote_repository.create(session, nuovo_quote)


# ── UPDATE STATUS 
def update_status(session, quote_id, data, is_admin=False):
    quote = get_by_id(session, quote_id)

    if "status" not in data:
        raise ValueError("Campo 'status' obbligatorio!")

    stati_validi = ["pending", "accepted", "rejected", "expired"]
    if data["status"] not in stati_validi:
        raise ValueError(f"Status deve essere uno di: {stati_validi}")

    quote.status = data["status"]

    return quote_repository.update(session, quote)


# ── DELETE 
def delete(session, quote_id, is_admin=False):

    if not is_admin:
        raise ValueError("Solo un admin può eliminare un preventivo!")

    quote = get_by_id(session, quote_id)

    # BUG FIX: rimette la configurazione in "draft" (non "saved")
    conf = quote.configuration
    if conf:
        conf.status = "draft"
        session.commit()

    quote_repository.delete_by_id(session, quote)