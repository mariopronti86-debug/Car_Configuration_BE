from flask import Blueprint, jsonify, request

from controller.auth_controller import token_required, role_required
from persistence.db_config import get_session
from service import engine_service

engine_bp = Blueprint("engine", __name__, url_prefix="/api/engines")


# ── GET /api/engines (pubblico)
@engine_bp.route("/", methods=["GET"])
def get_all():
    session = get_session()
    try:
        engines = engine_service.get_all(session)
        return jsonify([e.to_dict() for e in engines])
    finally:
        session.close()


# ── GET /api/engines/<id>
@engine_bp.route("/<int:engine_id>", methods=["GET"])
def get_by_id(engine_id):
    session = get_session()
    try:
        engine = engine_service.get_by_id(session, engine_id)
        return jsonify(engine.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    finally:
        session.close()


# ── POST /api/engines (solo admin)
@engine_bp.route("/", methods=["POST"])
@token_required
@role_required("admin")
def create():
    data = request.get_json()
    session = get_session()
    try:
        nuovo_engine = engine_service.create(session, data)
        return jsonify(nuovo_engine.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── PUT /api/engines/<id> (solo admin)
@engine_bp.route("/<int:engine_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update(engine_id):
    data = request.get_json()
    session = get_session()
    try:
        engine = engine_service.update(session, engine_id, data)
        return jsonify(engine.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── DELETE /api/engines/<id> (solo admin)
@engine_bp.route("/<int:engine_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete(engine_id):
    session = get_session()
    try:
        engine_service.delete(session, engine_id)
        return jsonify({"message": f"Engine {engine_id} eliminato!"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
