import datetime
import bcrypt
import jwt

from model.user import Client, Admin
from repository import user_repository

# Chiave usata per firmare i token JWT (in produzione va in .env!)
SECRET_KEY = "super-segreto-cambiami"


# ── Registrazione client
def register(session, data):

    if not data.get("first_name") or not data.get("last_name") or not data.get("email") or not data.get("password"):
        raise ValueError("Tutti i campi sono obbligatori!")

    if user_repository.get_by_email(session, data["email"]) is not None:
        raise ValueError("Email già registrata!")

    password_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    nuovo_client = Client(
        email=data["email"],
        password_hash=password_hash,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data.get("phone"),
    )

    return user_repository.create(session, nuovo_client)


# ── Creazione admin (solo un admin può creare altri admin)
def create_admin(session, data):

    if not data.get("email") or not data.get("password"):
        raise ValueError("Email e password obbligatori!")

    if user_repository.get_by_email(session, data["email"]) is not None:
        raise ValueError("Email già registrata!")

    password_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    nuovo_admin = Admin(email=data["email"], password_hash=password_hash)

    return user_repository.create(session, nuovo_admin)


# ── Login
def login(session, data):

    if not data.get("email") or not data.get("password"):
        raise ValueError("Email e password obbligatori!")

    utente = user_repository.get_by_email(session, data["email"])

    if utente is None:
        raise ValueError("Credenziali non valide!")

    password_valida = bcrypt.checkpw(data["password"].encode("utf-8"), utente.password_hash.encode("utf-8"))

    if not password_valida:
        raise ValueError("Credenziali non valide!")

    payload = {
        "user_id": utente.user_id,
        "email": utente.email,
        "ruolo": utente.type,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token, utente


def verifica_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token scaduto!")
    except jwt.InvalidTokenError:
        raise ValueError("Token non valido!")