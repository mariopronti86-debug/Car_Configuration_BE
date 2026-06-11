import datetime

from model.quote import Quote
from repository import quote_repository, configuration_repository
 
 
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
 
 
# ── GENERA PREVENTIVO
def genera_preventivo(session, configuration_id, client_id, data=None, is_admin=False):
 
    if data is None:
        data = {}
 
    conf = configuration_repository.get_by_id(session, configuration_id)
    if conf is None:
        raise ValueError(f"Configurazione con id={configuration_id} non trovata!")
 
    if not is_admin and conf.client_id != client_id:
        raise ValueError("Non sei autorizzato!")
 
    if conf.status == "quoted":
        raise ValueError("Esiste già un preventivo per questa configurazione!")
 
    discount_pct = float(data.get("discount_pct", 0))
    if discount_pct < 0 or discount_pct > 100:
        raise ValueError("Lo sconto deve essere tra 0 e 100!")
 
    final_price = round(float(conf.total_price) * (1 - discount_pct / 100), 2)
 
    # Numero progressivo: QT-2025-0001
    anno   = datetime.datetime.now().year
    ultimo = quote_repository.get_last(session)
    if ultimo is None:
        progressivo = 1
    else:
        try:
            progressivo = int(ultimo.quote_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            progressivo = 1
 
    nuovo_quote = Quote(
        quote_number=f"QT-{anno}-{progressivo:04d}",
        status="pending",
        final_price=final_price,
        discount_pct=discount_pct,
        configuration_id=configuration_id,
    )
 
    conf.status = "quoted"
    session.commit()
 
    return quote_repository.create(session, nuovo_quote)
 
 
# ── UPDATE STATUS
def update_status(session, quote_id, data):
    quote = get_by_id(session, quote_id)
 
    stati_validi = ["pending", "accepted", "rejected", "expired"]
    if data.get("status") not in stati_validi:
        raise ValueError(f"Status deve essere uno di: {stati_validi}")
 
    quote.status = data["status"]
    return quote_repository.update(session, quote)
 
 
# ── DELETE (solo admin)
def delete(session, quote_id):
    quote = get_by_id(session, quote_id)
 
    # Rimette la configurazione in "draft" così può essere riutilizzata
    if quote.configuration:
        quote.configuration.status = "draft"
        session.commit()
 
    quote_repository.delete_by_id(session, quote)