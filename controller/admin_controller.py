from flask import Blueprint, jsonify

from controller.auth_controller import token_required, role_required
from persistence.db_config import get_session
from repository import user_repository, car_model_repository, configuration_repository, quote_repository

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ── GET /api/admin/dashboard
@admin_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("admin")
def dashboard():
    session = get_session()
    try:
        clients = user_repository.get_all_clients(session)
        models = car_model_repository.get_all(session)
        configurations = configuration_repository.get_all(session)
        quotes = quote_repository.get_all(session)

        conf_per_stato  = {}
        for c in configurations:
            conf_per_stato[c.status] = conf_per_stato.get(c.status, 0) + 1

        quote_per_stato = {}
        for q in quotes:
            quote_per_stato[q.status] = quote_per_stato.get(q.status, 0) + 1

        fatturato = sum(float(q.final_price) for q in quotes if q.status == "accepted")

        return jsonify({
            "clienti": len(clients),
            "modelli": len(models),
            "configurazioni": {"totale": len(configurations), "per_stato": conf_per_stato},
            "preventivi": {"totale": len(quotes), "per_stato": quote_per_stato, "fatturato": round(fatturato, 2)},
        })
    finally:
        session.close()
