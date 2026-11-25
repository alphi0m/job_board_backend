# Bacheca Annunci di Lavoro - Backend

Progetto individuale per il corso di Enterprise Mobile Application Development (A.A. 2025/2026).
Sviluppato da Alfio Marra ([@alphi0m](https://github.com/alphi0m)).

## Descrizione
Il backend è un'applicazione REST sviluppata in Python con framework FastAPI. Gestisce la logica di business e la persistenza dei dati per una bacheca di annunci di lavoro, supportando due tipologie di utenti:
- **Aziende**: possono registrarsi, effettuare il login, pubblicare offerte di lavoro e consultare le candidature ricevute (inclusa la visualizzazione dei CV allegati).
- **Candidati**: possono visualizzare gli annunci disponibili e inviare candidature allegando il proprio Curriculum Vitae in formato PDF, senza necessità di registrazione.

I dati sono salvati in un database locale SQLite (`job_board.db`), mentre i file PDF dei curricula caricati dai candidati vengono archiviati nella directory `uploads/cvs/`.

## Requisiti di sistema
- Python 3.10 o superiore (testato su Python 3.14)
- pip

## Istruzioni per l'avvio

1. Clonare il repository:
```bash
git clone https://github.com/alphi0m/job_board_backend.git
cd job_board_backend
```

2. Creare e attivare l'ambiente virtuale:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installare le dipendenze:
```bash
pip install -r requirements.txt
```

4. Avviare il server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Il server sarà raggiungibile all'indirizzo `http://localhost:8000` (oppure tramite l'IP locale del computer per i dispositivi connessi alla stessa rete Wi-Fi).

La documentazione interattiva OpenAPI / Swagger è consultabile su:
- `http://localhost:8000/docs`

## Test automatici
Nel repository è presente uno script di test (`test_backend.py`) che verifica l'intero flusso degli scenari richiesti (registrazione azienda, login, pubblicazione annuncio, consultazione bacheca, candidatura con allegato PDF, consultazione candidature e download del CV):
```bash
python3 test_backend.py
```

## Struttura del codice
- `app/main.py`: configurazione dell'applicazione FastAPI, middleware CORS e registrazione dei router.
- `app/database.py`: connessione a SQLite tramite SQLAlchemy.
- `app/models.py`: definizione dei modelli di database (aziende, annunci, candidature).
- `app/schemas.py`: schemi Pydantic per validazione di input e serializzazione output.
- `app/auth.py`: gestione della sicurezza (hashing password con bcrypt e generazione token JWT).
- `app/routers/`: endpoint divisi per funzionalità (autenticazione, annunci, candidature).
- `uploads/cvs/`: cartella locale in cui vengono memorizzati i PDF caricati.
