# AutoElite – Backend API

Progetto finale del corso **Software Development 2025/2026**.

Piattaforma per la configurazione personalizzata di automobili con generazione di preventivi. Gli utenti possono selezionare modello, motorizzazione e optional, il sistema verifica le compatibilità tra componenti e calcola il prezzo in tempo reale.

---

## Tecnologie

| Layer | Tecnologia |
|---|---|
| Backend | Python / Flask |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Autenticazione | JWT (PyJWT) |
| Password | bcrypt |
| Architettura | MVC — Model / Repository / Service / Controller |

---

## Struttura del progetto

```
Car_Configuration_BE/
├── app.py                          # Entry point, registra tutti i blueprint
├── requirements.txt
│
├── persistence/
│   └── db_config.py                # Connessione DB, Base, init_db()
│
├── model/                          # Entità mappate su tabelle PostgreSQL
│   ├── user.py                     # User / Client / Admin (Joined Table Inheritance)
│   ├── engine.py                   # Motorizzazioni
│   ├── car_model.py                # Modelli auto (N:M con Optional)
│   ├── optional.py                 # Optional/accessori
│   ├── compatibility.py            # Regole di compatibilità tra optional
│   ├── configuration.py            # Configurazione utente (N:M con Optional)
│   └── quote.py                    # Preventivi
│
├── repository/                     # Accesso al DB — get_all / get_by_id / create / update / delete_by_id
│   └── ...
│
├── service/                        # Logica di business
│   └── ...
│
├── controller/                     # Blueprint Flask — routing e risposte HTTP
│   └── ...
│
└── docs/
    ├── DDL/10_CREATE.sql           # Crea tutte le tabelle
    └── DML/10_INSERT.sql           # Dati di esempio
```

---

## Installazione e avvio

### 1. Clona il progetto e installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Crea il database PostgreSQL

```bash
# Connettiti a PostgreSQL e crea il database
psql -U postgres

CREATE DATABASE car_config;
\q

# Esegui DDL e DML
psql -U postgres -d car_config -f docs/DDL/10_CREATE.sql
psql -U postgres -d car_config -f docs/DML/10_INSERT.sql
```

### 3. Configura la connessione

In `persistence/db_config.py` modifica la stringa di connessione con le tue credenziali:

```python
engine = create_engine("postgresql://postgres:TUA_PASSWORD@localhost/car_config", echo=True)
```

### 4. Avvia il server

```bash
python app.py
```

Il server parte su **http://localhost:5001**

---

## Credenziali di test

| Ruolo | Email | Password |
|---|---|---|
| Admin | admin@autoelite.it | Admin123! |
| Client | mario.rossi@email.com | Client123! |

---

## Autenticazione

Tutte le rotte protette richiedono il token JWT nell'header:

```
Authorization: Bearer <token>
```

Il token si ottiene con `POST /api/auth/login` e scade dopo **8 ore**.

---

## API Reference

### Auth — `/api/auth`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| POST | `/register` | Pubblico | Registra un nuovo client |
| POST | `/login` | Pubblico | Login — restituisce il token JWT |
| GET | `/me` | Client, Admin | Profilo dell'utente loggato |
| GET | `/users` | Admin | Lista tutti gli utenti |
| POST | `/admin` | Admin | Crea un nuovo admin |

**Esempio login:**
```json
POST /api/auth/login
{
  "email": "mario.rossi@email.com",
  "password": "Client123!"
}
```

**Risposta:**
```json
{
  "token": "eyJ...",
  "user": { "user_id": 2, "tipo": "client", "email": "mario.rossi@email.com" }
}
```

---

### Motorizzazioni — `/api/engines`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/` | Pubblico | Lista tutte le motorizzazioni |
| GET | `/<engine_id>` | Pubblico | Dettaglio motorizzazione |
| POST | `/` | Admin | Crea motorizzazione |
| PUT | `/<engine_id>` | Admin | Modifica motorizzazione |
| DELETE | `/<engine_id>` | Admin | Elimina motorizzazione |

---

### Modelli auto — `/api/models`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/` | Pubblico | Lista tutti i modelli |
| GET | `/<model_id>` | Pubblico | Dettaglio modello con optional disponibili |
| POST | `/` | Admin | Crea modello |
| PUT | `/<model_id>` | Admin | Modifica modello |
| DELETE | `/<model_id>` | Admin | Elimina modello |
| POST | `/<model_id>/optionals/<optional_id>` | Admin | Aggiunge optional al catalogo del modello |
| DELETE | `/<model_id>/optionals/<optional_id>` | Admin | Rimuove optional dal catalogo del modello |

---

### Optional — `/api/optionals`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/` | Pubblico | Lista tutti gli optional |
| GET | `/<optional_id>` | Pubblico | Dettaglio optional |
| GET | `/model/<model_id>` | Pubblico | Optional disponibili per un modello |
| POST | `/` | Admin | Crea optional |
| PUT | `/<optional_id>` | Admin | Modifica optional |
| DELETE | `/<optional_id>` | Admin | Elimina optional |

---

### Compatibilità — `/api/compatibility`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/rules` | Pubblico | Lista le regole (`incompatible`, `requires`) |
| POST | `/rules` | Admin | Crea una regola |
| DELETE | `/rules/<rule_id>` | Admin | Elimina una regola |
| GET | `/` | Pubblico | Lista tutte le regole tra optional |
| POST | `/` | Admin | Crea una regola tra due optional |
| DELETE | `/<compatibility_id>` | Admin | Elimina una regola tra optional |

**Tipi di regola:**
- `incompatible` — i due optional non possono essere scelti insieme
- `requires` — il primo optional richiede obbligatoriamente il secondo

---

### Configurazioni — `/api/configurations`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/` | Client, Admin | Lista configurazioni (client vede solo le sue) |
| GET | `/<configuration_id>` | Client, Admin | Dettaglio completo |
| POST | `/` | Client, Admin | Crea una nuova configurazione |
| PUT | `/<configuration_id>` | Client, Admin | Modifica configurazione |
| DELETE | `/<configuration_id>` | Client, Admin | Elimina configurazione |

**Esempio creazione configurazione:**
```json
POST /api/configurations
{
  "name": "La mia Audi",
  "model_id": 1,
  "engine_id": 2,
  "optional_ids": [3, 5, 9]
}
```

**Stati possibili:** `draft` → `saved` → `quoted`

> Una configurazione in stato `quoted` non può essere modificata.

---

### Preventivi — `/api/quotes`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/` | Client, Admin | Lista preventivi (client vede solo i suoi) |
| GET | `/<quote_id>` | Client, Admin | Dettaglio preventivo |
| GET | `/<quote_id>/export` | Client, Admin | Dati strutturati per stampa/PDF |
| POST | `/generate/<configuration_id>` | Client, Admin | Genera preventivo da una configurazione |
| PUT | `/<quote_id>/status` | Client, Admin | Aggiorna stato preventivo |
| DELETE | `/<quote_id>` | Admin | Elimina preventivo |

**Esempio generazione preventivo:**
```json
POST /api/quotes/generate/1
{
  "discount_pct": 5
}
```

**Stati preventivo:** `pending` → `accepted` / `rejected` / `expired`

> Il client può solo portare un preventivo a `accepted` o `rejected`.
> L'admin può impostare qualsiasi stato.

**Esempio export preventivo (`GET /api/quotes/1/export`):**
```json
{
  "preventivo": {
    "numero": "QT-2025-0001",
    "data": "15/01/2025",
    "stato": "pending",
    "prezzo_finale": 38665.00,
    "sconto_pct": 5.0
  },
  "cliente": {
    "nome": "Mario Rossi",
    "email": "mario.rossi@email.com",
    "telefono": "333-1234567"
  },
  "configurazione": {
    "nome": "La mia Audi",
    "marca": "Audi",
    "modello": "A3 Sportback",
    "prezzo_base": 35000.0,
    "motorizzazione": { "tipo": "Diesel", "potenza_cv": 200, "extra_prezzo": 2000.0 },
    "optional": [
      { "nome": "Tetto panoramico", "categoria": "Esterno", "prezzo": 2500.0 }
    ],
    "prezzo_totale": 40700.0
  }
}
```

---

### Dashboard Admin — `/api/admin`

| Metodo | Endpoint | Accesso | Descrizione |
|---|---|---|---|
| GET | `/dashboard` | Admin | Statistiche generali della piattaforma |

**Risposta:**
```json
{
  "clienti": 3,
  "modelli": 4,
  "configurazioni": { "totale": 12, "per_stato": { "draft": 5, "saved": 4, "quoted": 3 } },
  "preventivi": { "totale": 3, "per_stato": { "pending": 2, "accepted": 1 }, "fatturato": 38665.00 }
}
```

---

## Schema database

```
app_user ──< client ──< configuration >──< configuration_optional >── optional
                                │                                        │
                              model                               compatibility
                                │                                  (regole N:M
                             engine                               tra optional)
                                │
                             quote
```

**11 tabelle:** `app_user`, `client`, `admin`, `engine`, `model`, `optional`, `model_optional`, `compatibility_rule`, `compatibility`, `configuration`, `configuration_optional`, `quote`

---

## Gestione errori

Tutti gli errori restituiscono JSON con il campo `error`:

```json
{ "error": "Descrizione del problema" }
```

| Codice | Significato |
|---|---|
| 400 | Dati non validi o regola di business violata |
| 401 | Token mancante o non valido |
| 403 | Accesso negato (ruolo insufficiente) |
| 404 | Risorsa non trovata |