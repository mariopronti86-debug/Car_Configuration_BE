from flask import Blueprint, jsonify, request

from controller.auth_controller import token_required, role_required
from persistence.db_config import get_session
from service import compatibility_service

compatibility_bp = Blueprint("compatibility", __name__, url_prefix="/api/compatibility")


# ── GET /api/compatibility/rules (pubblico)
@compatibility_bp.route("/rules", methods=["GET"])
def get_all_rules():
    session = get_session()
    try:
        rules = compatibility_service.get_all_rules(session)
        return jsonify([r.to_dict() for r in rules])
    finally:
        session.close()


# ── POST /api/compatibility/rules (solo admin)
@compatibility_bp.route("/rules", methods=["POST"])
@token_required
@role_required("admin")
def create_rule():
    data = request.get_json()
    session = get_session()
    try:
        nuova_rule = compatibility_service.create_rule(session, data)
        return jsonify(nuova_rule.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── DELETE /api/compatibility/rules/<id> (solo admin)
@compatibility_bp.route("/rules/<int:rule_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_rule(rule_id):
    session = get_session()
    try:
        compatibility_service.delete_rule(session, rule_id)
        return jsonify({"message": f"Regola {rule_id} eliminata!"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── GET /api/compatibility (pubblico)
@compatibility_bp.route("/", methods=["GET"])
def get_all():
    session = get_session()
    try:
        compatibilities = compatibility_service.get_all(session)
        return jsonify([c.to_dict() for c in compatibilities])
    finally:
        session.close()


# ── POST /api/compatibility (solo admin)
@compatibility_bp.route("/", methods=["POST"])
@token_required
@role_required("admin")
def create():
    data = request.get_json()
    session = get_session()
    try:
        nuova_comp = compatibility_service.create(session, data)
        return jsonify(nuova_comp.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── DELETE /api/compatibility/<id> (solo admin)
@compatibility_bp.route("/<int:compatibility_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete(compatibility_id):
    session = get_session()
    try:
        compatibility_service.delete(session, compatibility_id)
        return jsonify({"message": f"Compatibility {compatibility_id} eliminata!"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
