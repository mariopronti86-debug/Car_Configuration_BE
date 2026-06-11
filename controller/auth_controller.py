from functools import wraps
from flask import Blueprint, g, jsonify, request


from persistence.db_config import get_session
from repository import user_repository
from service import auth_service

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── POST /api/auth/register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    session = get_session()

    try:
        nuovo_client = auth_service.register(session, data)
        return jsonify(nuovo_client.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


# ── POST /api/auth/login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    session = get_session()

    try:
        token, utente = auth_service.login(session, data)
        return jsonify({"token": token, "user": utente.to_dict()})
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    finally:
        session.close()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            parti = request.headers["Authorization"].split(" ")
            if len(parti) == 2 and parti[0] == "Bearer":
                token = parti[1]

        if token is None:
            return jsonify({"error": "Token mancante!"}), 401

        try:
            payload = auth_service.verifica_token(token)
            g.user_id = payload["user_id"]
            g.user_email = payload["email"]
            g.user_ruolo = payload["ruolo"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated


def role_required(*ruoli_ammessi):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.user_ruolo not in ruoli_ammessi:
                return jsonify({"error": "Accesso negato!"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── GET /api/auth/me
@auth_bp.route("/me")
@token_required
@role_required("admin", "client")
def me():
    session = get_session()

    try:
        utente = user_repository.get_by_id(session, g.user_id)
        return jsonify(utente.to_dict())
    finally:
        session.close()


# ── GET /api/auth/users (solo admin)
@auth_bp.route("/users")
@token_required
@role_required("admin")
def get_all_users():
    session = get_session()

    try:
        clients = user_repository.get_all_clients(session)
        admins  = user_repository.get_all_admins(session)
        return jsonify({
            "clients": [u.to_dict() for u in clients],
            "admins":  [u.to_dict() for u in admins],
        })
    finally:
        session.close()


# ── POST /api/auth/admin (solo admin)
@auth_bp.route("/admin", methods=["POST"])
@token_required
@role_required("admin")
def create_admin():
    data = request.get_json()
    session = get_session()

    try:
        nuovo_admin = auth_service.create_admin(session, data)
        return jsonify(nuovo_admin.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()
