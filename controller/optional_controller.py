from flask import Blueprint, jsonify, request

from controller.auth_controller import token_required, role_required
from persistence.db_config import get_session
from service import optional_service

optional_bp = Blueprint("optional", __name__, url_prefix="/api/optionals")


# ── GET /api/optionals (pubblico)
@optional_bp.route("/", methods=["GET"])
def get_all():
    session = get_session()
    try:
        optionals = optional_service.get_all(session)
        return jsonify([o.to_dict() for o in optionals])
    finally:
        session.close()


# ── GET /api/optionals/<id>
@optional_bp.route("/<int:optional_id>", methods=["GET"])
def get_by_id(optional_id):
    session = get_session()
    try:
        optional = optional_service.get_by_id(session, optional_id)
        return jsonify(optional.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        session.close()


# ── GET /api/optionals/model/<model_id> — optional disponibili per un modello
@optional_bp.route("/model/<int:model_id>", methods=["GET"])
def get_by_model(model_id):
    session = get_session()
    try:
        optionals = optional_service.get_by_model(session, model_id)
        return jsonify([o.to_dict() for o in optionals])
    finally:
        session.close()


# ── POST /api/optionals (solo admin)
@optional_bp.route("/", methods=["POST"])
@token_required
@role_required("admin")
def create():
    data = request.get_json()
    session = get_session()
    try:
        nuovo_optional = optional_service.create(session, data)
        return jsonify(nuovo_optional.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── PUT /api/optionals/<id> (solo admin)
@optional_bp.route("/<int:optional_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update(optional_id):
    data = request.get_json()
    session = get_session()
    try:
        optional = optional_service.update(session, optional_id, data)
        return jsonify(optional.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── DELETE /api/optionals/<id> (solo admin)
@optional_bp.route("/<int:optional_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete(optional_id):
    session = get_session()
    try:
        optional_service.delete(session, optional_id)
        return jsonify({"message": f"Optional {optional_id} eliminato!"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
