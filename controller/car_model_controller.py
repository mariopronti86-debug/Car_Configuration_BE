from flask import Blueprint, jsonify, request

from controller.auth_controller import token_required, role_required
from persistence.db_config import get_session
from service import car_model_service

car_model_bp = Blueprint("car_model", __name__, url_prefix="/api/models")


# GET /api/models (pubblico)
@car_model_bp.route("/", methods=["GET"])
def get_all():
    session = get_session()
    try:
        models = car_model_service.get_all(session)
        return jsonify([m.to_dict() for m in models])
    finally:
        session.close()


# GET /api/models/<id> —-> dettaglio con optional disponibili
@car_model_bp.route("/<int:model_id>", methods=["GET"])
def get_by_id(model_id):
    session = get_session()
    try:
        car_model = car_model_service.get_by_id(session, model_id)
        return jsonify(car_model.to_dict_full())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        session.close()


# POST /api/models (solo admin)
@car_model_bp.route("/", methods=["POST"])
@token_required
@role_required("admin")
def create():
    data = request.get_json()
    session = get_session()
    try:
        nuovo_modello = car_model_service.create(session, data)
        return jsonify(nuovo_modello.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# PUT /api/models/<id> (solo admin)
@car_model_bp.route("/<int:model_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update(model_id):
    data = request.get_json()
    session = get_session()
    try:
        modello = car_model_service.update(session, model_id, data)
        return jsonify(modello.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# DELETE /api/models/<id> (solo admin)
@car_model_bp.route("/<int:model_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete(model_id):
    session = get_session()
    try:
        car_model_service.delete(session, model_id)
        return jsonify({"message": f"Modello {model_id} eliminato!"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# POST /api/models/<id>/optionals/<opt_id> (solo admin)
@car_model_bp.route("/<int:model_id>/optionals/<int:optional_id>", methods=["POST"])
@token_required
@role_required("admin")
def add_optional(model_id, optional_id):
    session = get_session()
    try:
        modello = car_model_service.add_optional(session, model_id, optional_id)
        return jsonify(modello.to_dict_full())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# DELETE /api/models/<id>/optionals/<opt_id> (solo admin)
@car_model_bp.route("/<int:model_id>/optionals/<int:optional_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def remove_optional(model_id, optional_id):
    session = get_session()
    try:
        modello = car_model_service.remove_optional(session, model_id, optional_id)
        return jsonify(modello.to_dict_full())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
