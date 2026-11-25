# Job Board Backend (Bacheca Annunci di Lavoro)

Backend REST API sviluppato per il corso di **Enterprise Mobile Application Development**.
Il server gestisce l'autenticazione delle aziende, la pubblicazione e consultazione degli annunci di lavoro, la ricezione delle candidature e l'archiviazione su disco e database dei Curriculum Vitae (PDF).

## 🚀 Architettura e Tecnologie
- **Linguaggio**: Python 3.14
- **Framework**: FastAPI (asincrono, standard OpenAPI / Swagger)
- **Database**: SQLite (persistente su file locale `job_board.db`)
- **ORM**: SQLAlchemy
- **Autenticazione**: JSON Web Token (JWT) e password hashing con `bcrypt`
- **File Upload**: `python-multipart` con storage sicuro in `uploads/cvs/`

---

## 📋 Requisiti Funzionali Soddisfatti
- **R1 – Registrazione (azienda)**: `POST /api/auth/register`
- **R2 – Login (azienda)**: `POST /api/auth/login`
- **R3 – Logout (azienda)**: `POST /api/auth/logout`
- **R4 – Pubblicazione annuncio (azienda)**: `POST /api/jobs`
- **R5 – Consultazione bacheca (candidato)**: `GET /api/jobs` e `GET /api/jobs/{id}`
- **R6 – Candidatura (candidato)**: `POST /api/jobs/{id}/apply` (Multipart form-data con file PDF)
- **R7 – Consultazione candidature (azienda)**: `GET /api/company/my-jobs`, `GET /api/jobs/{id}/applications` e `GET /api/uploads/cv/{filename}`

---

## 🛠️ Installazione e Avvio Rapido

### 1. Clonare il repository e creare il virtual environment
```bash
git clone <url-repo-backend>
cd job_board_backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Avviare il Server
```bash
# Avvio in ascolto su tutte le interfacce di rete (0.0.0.0), porta 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
> [!NOTE]
> L'ascolto su `0.0.0.0` permette allo smartphone connesso alla stessa rete Wi-Fi di comunicare con il server tramite l'IP locale del computer (es. `http://192.168.1.X:8000`).

### 3. Documentazione Interattiva Swagger
A server avviato, aprire nel browser:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Esecuzione dei Test Automatici
Il repository include uno script di collaudo end-to-end che valida l'intero ciclo di vita degli Scenari S1, S2 e S3:
```bash
source venv/bin/activate
python3 test_backend.py
```
Output atteso:
```text
[SCENARIO S1] Test Registrazione Azienda (R1)... ✓
[SCENARIO S1] Test Login Azienda (R2)... ✓
[SCENARIO S1] Test Pubblicazione Annuncio (R4)... ✓
[SCENARIO S2] Test Consultazione Bacheca Pubblica (R5)... ✓
[SCENARIO S2] Test Dettaglio Annuncio (R5)... ✓
[SCENARIO S2] Test Invio Candidatura con CV in PDF (R6)... ✓
[SCENARIO S3] Test Elenco Miei Annunci con Conteggio (R7)... ✓
[SCENARIO S3] Test Consultazione Candidature per Annuncio (R7)... ✓
[SCENARIO S3] Test Download e Apertura Curriculum PDF (R7)... ✓
[SCENARIO S3] Test Access Control e Sicurezza... ✓
[SCENARIO S3] Test Logout Azienda (R3)... ✓
[PERSISTENZA] Test persistenza dati su SQLite... ✓
```

---

## 📂 Struttura del Progetto
```text
job_board_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # Setup FastAPI, CORS e lifecycle
│   ├── database.py            # Connessione SQLite e SessionLocal
│   ├── models.py              # Modelli SQLAlchemy (Company, Job, Application)
│   ├── schemas.py             # Schemi Pydantic di input/output
│   ├── auth.py                # Hashing password e generazione/verifica JWT
│   └── routers/
│       ├── __init__.py
│       ├── auth_router.py     # Endpoint registrazione e login
│       ├── jobs_router.py     # Endpoint annunci pubblici e aziendali
│       └── applications_router.py # Endpoint candidatura e gestione CV
├── uploads/
│   └── cvs/                   # Directory di archiviazione file PDF
├── requirements.txt           # Dipendenze Python
├── test_backend.py            # Suite di test end-to-end
├── .gitignore
└── README.md
```
