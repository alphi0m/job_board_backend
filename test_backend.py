"""
Script di collaudo automatico per il backend di 'Bacheca Annunci di Lavoro'.
Verifica i requisiti R1-R7 e gli scenari S1-S3 tramite TestClient di FastAPI.
"""
import io
import os
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Company, Job, Application

client = TestClient(app)


def test_full_scenario_lifecycle():
    print("\n--- Inizio Collaudo Backend ---")

    # 1. Reset / Init DB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # -------------------------------------------------------------
    # SCENARIO S1: Registrazione, Login, Pubblicazione Annuncio
    # -------------------------------------------------------------
    print("\n[SCENARIO S1] Test Registrazione Azienda (R1)...")
    reg_payload = {
        "name": "TechCorp S.r.l.",
        "email": "info@techcorp.it",
        "password": "PasswordSicura123!"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201, f"Errore registrazione: {res.text}"
    comp_data = res.json()
    assert comp_data["email"] == "info@techcorp.it"
    assert comp_data["name"] == "TechCorp S.r.l."
    print("✓ R1 superato con successo.")

    print("\n[SCENARIO S1] Test Login Azienda (R2)...")
    login_payload = {
        "email": "info@techcorp.it",
        "password": "PasswordSicura123!"
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200, f"Errore login: {res.text}"
    token_data = res.json()
    token = token_data["access_token"]
    assert token is not None
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("✓ R2 superato: Token JWT ricevuto.")

    print("\n[SCENARIO S1] Test Pubblicazione Annuncio (R4)...")
    job_payload = {
        "title": "Flutter Mobile Developer",
        "description": "Cerchiamo sviluppatore Flutter junior/mid per applicazioni enterprise. Requisiti: Dart, State Management, REST API.",
        "location": "Salerno / Ibrido"
    }
    res = client.post("/api/jobs", json=job_payload, headers=auth_headers)
    assert res.status_code == 201, f"Errore creazione annuncio: {res.text}"
    job_created = res.json()
    job_id = job_created["id"]
    assert job_created["title"] == job_payload["title"]
    assert job_created["company_name"] == "TechCorp S.r.l."
    print(f"✓ R4 superato: Annuncio #{job_id} creato con successo.")

    # -------------------------------------------------------------
    # SCENARIO S2: Consultazione Bacheca e Candidatura con PDF
    # -------------------------------------------------------------
    print("\n[SCENARIO S2] Test Consultazione Bacheca Pubblica (R5 - Senza Auth)...")
    res = client.get("/api/jobs")
    assert res.status_code == 200
    public_jobs = res.json()
    assert len(public_jobs) == 1
    assert public_jobs[0]["id"] == job_id
    print("✓ R5 (Elenco) superato: L'annuncio appare nella bacheca pubblica.")

    print("\n[SCENARIO S2] Test Dettaglio Annuncio (R5)...")
    res = client.get(f"/api/jobs/{job_id}")
    assert res.status_code == 200
    job_detail = res.json()
    assert job_detail["id"] == job_id
    assert "Flutter" in job_detail["title"]
    print("✓ R5 (Dettaglio) superato.")

    print("\n[SCENARIO S2] Test Invio Candidatura con CV in PDF (R6 - Senza Auth)...")
    fake_pdf_content = b"%PDF-1.4 Mock PDF CV Content for Candidate Mario Rossi"
    files = {
        "cv": ("curriculum_mario_rossi.pdf", io.BytesIO(fake_pdf_content), "application/pdf")
    }
    form_data = {
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario.rossi@studenti.unisa.it"
    }
    res = client.post(f"/api/jobs/{job_id}/apply", data=form_data, files=files)
    assert res.status_code == 201, f"Errore candidatura: {res.text}"
    app_res = res.json()
    assert "successo" in app_res["message"].lower()
    print("✓ R6 superato: Candidatura e file PDF registrati sul server.")

    # -------------------------------------------------------------
    # SCENARIO S3: Consultazione Candidature, Apertura CV e Logout
    # -------------------------------------------------------------
    print("\n[SCENARIO S3] Test Elenco Miei Annunci con Conteggio (R7)...")
    res = client.get("/api/company/my-jobs", headers=auth_headers)
    assert res.status_code == 200
    my_jobs = res.json()
    assert len(my_jobs) == 1
    assert my_jobs[0]["applications_count"] == 1
    print("✓ R7 (Conteggio) superato: 1 candidatura conteggiata.")

    print("\n[SCENARIO S3] Test Consultazione Candidature per Annuncio (R7)...")
    res = client.get(f"/api/jobs/{job_id}/applications", headers=auth_headers)
    assert res.status_code == 200
    applications = res.json()
    assert len(applications) == 1
    applicant = applications[0]
    assert applicant["first_name"] == "Mario"
    assert applicant["last_name"] == "Rossi"
    assert applicant["email"] == "mario.rossi@studenti.unisa.it"
    cv_url = applicant["cv_url"]
    assert "curriculum_mario_rossi.pdf" in applicant["cv_original_name"]
    print(f"✓ R7 (Elenco Candidature) superato. URL CV: {cv_url}")

    print("\n[SCENARIO S3] Test Download e Apertura Curriculum PDF (R7)...")
    cv_filename = applicant["cv_filename"]
    res = client.get(f"/api/uploads/cv/{cv_filename}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content == fake_pdf_content
    print("✓ R7 (Apertura CV) superato: Contenuto del PDF letto e integro.")

    print("\n[SCENARIO S3] Test Access Control e Sicurezza...")
    # Accesso senza token alle candidature -> deve fallire (401)
    unauth_res = client.get(f"/api/jobs/{job_id}/applications")
    assert unauth_res.status_code == 401
    print("✓ Protezione endpoint verificata: 401 Unauthorized su route protetta.")

    print("\n[SCENARIO S3] Test Logout Azienda (R3)...")
    res = client.post("/api/auth/logout", headers=auth_headers)
    assert res.status_code == 200
    print("✓ R3 superato: Logout effettuato con successo.")

    # -------------------------------------------------------------
    # TEST PERSISTENZA: Riavvio client/sessione
    # -------------------------------------------------------------
    print("\n[PERSISTENZA] Test persistenza dati su SQLite...")
    # Creiamo una nuova istanza TestClient senza toccare il DB
    new_client = TestClient(app)
    res = new_client.get("/api/jobs")
    assert res.status_code == 200
    jobs_after_restart = res.json()
    assert len(jobs_after_restart) >= 1
    assert jobs_after_restart[0]["title"] == "Flutter Mobile Developer"
    print("✓ Persistenza verificata: i dati restano integri nel file SQLite.")

    print("\n==============================================")
    print("TUTTI I REQUISITI (R1-R7) E SCENARI (S1-S3) VERIFICATI CON SUCCESSO!")
    print("==============================================")


if __name__ == "__main__":
    test_full_scenario_lifecycle()
