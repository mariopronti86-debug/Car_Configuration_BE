import datetime
import bcrypt
import jwt
 
from model.user import Client, Admin
from repository import user_repository
 
SECRET_KEY = "cambiami-in-produzione"
 
 
def register(session, data):
    for campo in ["first_name", "last_name", "email", "password"]:
        if campo not in data or len(str(data[campo]).strip()) == 0:
            raise ValueError(f"Campo '{campo}' obbligatorio!")
 
    if len(data["password"]) < 4:
        raise ValueError("Password troppo corta! (minimo 4 caratteri)")
 
    if user_repository.get_by_email(session, data["email"]) is not None:
        raise ValueError("Email già registrata!")
 
    hash_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    client = Client(
                    email=data["email"],
                    password_hash=hash_pw,
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    phone=data.get("phone")
                    )
    
    return user_repository.create(session, client)

# ADMIN
 
def create_admin(session, data):
     for campo in ["email", "password"]:
        if campo not in data or len(str(data[campo]).strip()) == 0:
            raise ValueError(f"Campo '{campo}' obbligatorio!")
 
        if user_repository.get_by_email(session, data["email"])is not None:
            raise ValueError("Email già registrata!")
 
        hash_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        admin = Admin(email=data["email"], password_hash=hash_pw)
        return user_repository.create(session, admin)
 
 
#LOGIN

def login(session, data):

    if "email" not in data or "password" not in data:
        raise ValueError("Email e password obbligatori!")
 
    utente = user_repository.get_by_email(session, data["email"])

    if utente is None:
        raise ValueError("Credenziali non valide!")
    
    pw_valid = bcrypt.checkpw(data["password"].encode("utf-8"), utente.password_hash.encode("utf-8"))
 
    if not pw_valid:
        raise ValueError("Credenziali non valide!")
 
    payload = {
        "user_id": utente.user_id,
        "email": utente.email,
        "ruolo": utente.tipo,
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