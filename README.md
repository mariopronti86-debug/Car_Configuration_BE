# Configuratore Auto — Backend Documentation

## Stack
- **Flask** — framework HTTP
- **SQLAlchemy** — ORM con Joined Table Inheritance
- **PostgreSQL** — database relazionale
- **PyJWT + bcrypt** — autenticazione JWT e hashing password

---

## Struttura del Progetto

```
car_config/
├── app.py                          # Entry point Flask
├── requirements.txt
├── persistence/
│   └── db_config.py                # Engine SQLAlchemy, init_db, get_session
├── model/
│   ├── user.py                     # User (base) → Client, Admin  [ISA]
│   ├── engine.py                   # Engine (motorizzazione)
│   ├── car_model.py                # CarModel (modello auto)
│   ├── optional.py                 # Optional + tabella model_optional
│   ├── compatibility.py            # Compatibility + CompatibilityRule
│   ├── configuration.py            # Configuration + tabella configuration_optional
│   └── quote.py                    # Quote (preventivo)
├── repository/
│   ├── user_repository.py
│   ├── engine_repository.py
│   ├── car_model_repository.py
│   ├── optional_repository.py
│   ├── compatibility_repository.py
│   ├── configuration_repository.py
│   └── quote_repository.py
├── service/
│   ├── auth_service.py
│   ├── engine_service.py
│   ├── car_model_service.py
│   ├── optional_service.py
│   ├── compatibility_service.py
│   ├── configuration_service.py
│   └── quote_service.py
├── controller/
│   ├── auth_controller.py          # Decorators token_required, role_required
│   ├── engine_controller.py
│   ├── car_model_controller.py
│   ├── optional_controller.py
│   ├── compatibility_controller.py
│   ├── configuration_controller.py
│   └── quote_controller.py
└── docs/
    ├── DDL.sql
    └── README.md
```

---

## Setup

```bash
# 1. Crea il database
createdb car_config;

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. (Opzionale) modifica la stringa di connessione in persistence/db_config.py

# 4. Avvia l'app (crea le tabelle automaticamente)
python app.py
```

---

## API Reference

### Auth  `/api/auth`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| POST | `/register` | — | Registra un nuovo client |
| POST | `/login` | — | Login, restituisce JWT |
| GET | `/me` | client/admin | Dati utente corrente |
| GET | `/users` | admin | Lista tutti i client e admin |
| POST | `/admin` | admin | Crea un nuovo admin |

**Register body:**
```json
{ "first_name": "Mario", "last_name": "Rossi", "email": "mario@example.com", "password": "1234" }
```

**Login body / risposta:**
```json
// request
{ "email": "mario@example.com", "password": "1234" }
// response
{ "token": "eyJ...", "user": { "user_id": 1, "tipo": "client", ... } }
```

---

### Engine  `/api/engines`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| GET | `/` | — | Lista motori |
| GET | `/<id>` | — | Dettaglio motore |
| POST | `/` | admin | Crea motore |
| PUT | `/<id>` | admin | Aggiorna motore |
| DELETE | `/<id>` | admin | Elimina motore |

---

### CarModel  `/api/models`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| GET | `/` | — | Lista modelli (con engine) |
| GET | `/<id>` | — | Dettaglio modello |
| GET | `/<id>/optionals` | — | Optional disponibili per modello |
| POST | `/` | admin | Crea modello |
| PUT | `/<id>` | admin | Aggiorna modello |
| DELETE | `/<id>` | admin | Elimina modello |
| POST | `/<id>/optionals/<opt_id>` | admin | Aggiunge optional al modello |
| DELETE | `/<id>/optionals/<opt_id>` | admin | Rimuove optional dal modello |

---

### Optional  `/api/optionals`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| GET | `/` | — | Lista optional |
| GET | `/<id>` | — | Dettaglio optional |
| POST | `/` | admin | Crea optional |
| PUT | `/<id>` | admin | Aggiorna optional |
| DELETE | `/<id>` | admin | Elimina optional |

---

### Compatibility  `/api/compatibility`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| GET | `/rules` | admin | Lista regole |
| POST | `/rules` | admin | Crea regola (`rule_type`: `incompatible` \| `requires`) |
| DELETE | `/rules/<id>` | admin | Elimina regola |
| GET | `/` | admin | Lista compatibility entries |
| POST | `/` | admin | Crea entry (`optional_id`, `optional_with_id`, `rule_id`) |
| DELETE | `/<id>` | admin | Elimina entry |
| POST | `/check` | client/admin | Verifica lista optional (`{"optional_ids": [1,2,3]}`) |

---

### Configuration  `/api/configurations`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| GET | `/` | client/admin | Lista configurazioni (client: solo proprie) |
| GET | `/<id>` | client/admin | Dettaglio configurazione |
| POST | `/` | client | Crea configurazione |
| PUT | `/<id>` | client/admin | Aggiorna configurazione |
| DELETE | `/<id>` | client/admin | Elimina configurazione |

**Create body:**
```json
{
  "name": "La mia Stelvio",
  "model_id": 2,
  "engine_id": 3,
  "optional_ids": [1, 3, 5]
}
```

---

### Quote  `/api/quotes`

| Metodo | URL | Auth | Descrizione |
|--------|-----|------|-------------|
| GET | `/` | client/admin | Lista preventivi (client: solo propri) |
| GET | `/<id>` | client/admin | Dettaglio preventivo |
| POST | `/generate/<configuration_id>` | client/admin | Genera preventivo da configurazione |
| PUT | `/<id>/status` | client/admin | Aggiorna status |
| DELETE | `/<id>` | admin | Elimina preventivo |

**Generate body (opzionale):**
```json
{ "discount_pct": 5.0 }
```

**Update status body:**
```json
{ "status": "accepted" }
```
Status validi: `pending` | `accepted` | `rejected` | `expired`

---

## Autenticazione

Tutte le rotte protette richiedono l'header:
```
Authorization: Bearer <token>
```

Il token JWT contiene: `user_id`, `email`, `ruolo` (`client` | `admin`), scadenza (8h).

---

## Scelte Progettuali

### ISA (User → Client / Admin)
Implementata con **Joined Table Inheritance** di SQLAlchemy, fedele al diagramma ER. La colonna `tipo` in `app_user` è il discriminante. Client e Admin hanno tabelle separate con campi specifici.

### Calcolo Prezzo
Il `total_price` di una Configuration è calcolato nel service: `base_price (modello) + extra_price (motore) + Σ price (optional selezionati)`. Viene ricalcolato ad ogni update.

### Compatibilità
Due tipologie di regole:
- **incompatible**: i due optional non possono coesistere nella stessa configurazione
- **requires**: se A è selezionato, B deve essere presente

La verifica avviene nel `compatibility_service.check_optional_list()` prima di salvare o aggiornare una configurazione.

### Autorizzazioni
- **Admin**: accesso completo a tutti gli endpoint, CRUD su catalogo, visione di tutte le configurazioni/preventivi
- **Client**: può creare/modificare/eliminare solo le proprie configurazioni, generare e accettare/rifiutare i propri preventivi
- **Pubblico**: lettura del catalogo (modelli, motori, optional) per supportare il frontend del configuratore

## Autore
Mario Pronti — Corso Software Development 2025/2026