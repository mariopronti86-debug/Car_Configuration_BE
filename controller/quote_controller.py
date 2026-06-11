from flask import Blueprint, g, jsonify, request

from controller.auth_controller import token_required, role_required
from persistence.db_config import get_session
from service import quote_service

quote_bp = Blueprint("quote", __name__, url_prefix="/api/quotes")


# ── GET /api/quotes — admin vede tutto, client vede solo i suoi
@quote_bp.route("/", methods=["GET"])
@token_required
@role_required("client", "admin")
def get_all():
    session = get_session()
    try:
        if g.user_ruolo == "admin":
            quotes = quote_service.get_all(session)
        else:
            quotes = quote_service.get_by_client(session, g.user_id)
        return jsonify([q.to_dict() for q in quotes])
    finally:
        session.close()


# ── GET /api/quotes/<id>
@quote_bp.route("/<int:quote_id>", methods=["GET"])
@token_required
@role_required("client", "admin")
def get_by_id(quote_id):
    session = get_session()
    try:
        quote = quote_service.get_by_id(session, quote_id)

        if g.user_ruolo == "client" and quote.configuration.client_id != g.user_id:
            return jsonify({"error": "Accesso negato!"}), 403

        return jsonify(quote.to_dict_full())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        session.close()


# ── GET /api/quotes/<id>/export — dati strutturati per stampa/PDF
@quote_bp.route("/<int:quote_id>/export", methods=["GET"])
@token_required
@role_required("client", "admin")
def export(quote_id):
    session = get_session()
    try:
        quote = quote_service.get_by_id(session, quote_id)

        if g.user_ruolo == "client" and quote.configuration.client_id != g.user_id:
            return jsonify({"error": "Accesso negato!"}), 403

        conf   = quote.configuration
        client = conf.client

        return jsonify({
            "preventivo": {
                "numero":        quote.quote_number,
                "data":          quote.issued_at.strftime("%d/%m/%Y") if quote.issued_at else None,
                "stato":         quote.status,
                "prezzo_finale": float(quote.final_price),
                "sconto_pct":    float(quote.discount_pct),
            },
            "cliente": {
                "nome":     f"{client.first_name} {client.last_name}" if client else "N/D",
                "email":    client.email if client else "N/D",
                "telefono": client.phone if client else "N/D",
            },
            "configurazione": {
                "nome":        conf.name,
                "marca":       conf.car_model.brand if conf.car_model else "N/D",
                "modello":     conf.car_model.name if conf.car_model else "N/D",
                "prezzo_base": float(conf.car_model.base_price) if conf.car_model else 0,
                "motorizzazione": {
                    "tipo":         conf.engine.fuel_type if conf.engine else "N/D",
                    "potenza_cv":   conf.engine.power_hp if conf.engine else 0,
                    "extra_prezzo": float(conf.engine.extra_price) if conf.engine else 0,
                },
                "optional": [{"nome": o.name, "categoria": o.category, "prezzo": float(o.price)} for o in conf.optionals],
                "prezzo_totale": float(conf.total_price),
            },
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        session.close()


# ── POST /api/quotes/generate/<configuration_id>
@quote_bp.route("/generate/<int:configuration_id>", methods=["POST"])
@token_required
@role_required("client", "admin")
def genera(configuration_id):
    data = request.get_json() or {}
    session = get_session()
    try:
        quote = quote_service.genera_preventivo(
            session, configuration_id,
            g.user_id, data,
            is_admin=(g.user_ruolo == "admin")
        )
        return jsonify(quote.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── PUT /api/quotes/<id>/status
@quote_bp.route("/<int:quote_id>/status", methods=["PUT"])
@token_required
@role_required("client", "admin")
def update_status(quote_id):
    data = request.get_json()
    session = get_session()
    try:
        # Il client può solo accettare o rifiutare i suoi preventivi
        if g.user_ruolo == "client":
            quote = quote_service.get_by_id(session, quote_id)
            if quote.configuration.client_id != g.user_id:
                return jsonify({"error": "Accesso negato!"}), 403
            if data.get("status") not in ["accepted", "rejected"]:
                return jsonify({"error": "Il client può solo accettare o rifiutare!"}), 403

        quote = quote_service.update_status(session, quote_id, data)
        return jsonify(quote.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── DELETE /api/quotes/<id> (solo admin)
@quote_bp.route("/<int:quote_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete(quote_id):
    session = get_session()
    try:
        quote_service.delete(session, quote_id)
        return jsonify({"message": f"Preventivo {quote_id} eliminato!"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
