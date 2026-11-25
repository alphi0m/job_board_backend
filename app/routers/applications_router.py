import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job, Application, Company
from ..schemas import ApplicationOut, ApplicationSuccess
from ..auth import get_current_company

router = APIRouter(tags=["Candidature"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "cvs")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/jobs/{job_id}/apply", response_model=ApplicationSuccess, status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    job_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    cv: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Candidatura a un annuncio con upload del Curriculum Vitae (R6 - Candidato senza login)."""
    # 1. Verifica esistenza annuncio
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annuncio di lavoro non trovato.",
        )

    # 2. Validazione campi
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()
    if not first_name or not last_name or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome, cognome ed email sono obbligatori.",
        )

    # 3. Validazione file
    original_filename = cv.filename or "cv.pdf"
    ext = os.path.splitext(original_filename)[1].lower()
    if not ext:
        ext = ".pdf"

    # Genera un nome file univoco per evitare collisioni
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    target_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Salva il file sul disco del server
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(cv.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nel salvataggio del file: {str(e)}",
        )
    finally:
        await cv.close()

    # 4. Registrazione candidatura nel database
    application = Application(
        job_id=job.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        cv_filename=unique_filename,
        cv_original_name=original_filename,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return ApplicationSuccess(
        message="Candidatura registrata con successo!",
        application_id=application.id,
    )


@router.get("/jobs/{job_id}/applications", response_model=List[ApplicationOut])
def get_job_applications(
    job_id: int,
    request: Request,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """Consultazione delle candidature ricevute per un proprio annuncio (R7 - Azienda autenticata)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annuncio di lavoro non trovato.",
        )

    # Verifica che l'annuncio appartenga all'azienda autenticata
    if job.company_id != current_company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai i permessi per visualizzare le candidature di questo annuncio.",
        )

    applications = (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
        .all()
    )

    base_url = str(request.base_url).rstrip("/")

    result = []
    for app in applications:
        cv_url = f"{base_url}/api/uploads/cv/{app.cv_filename}"
        result.append(
            ApplicationOut(
                id=app.id,
                job_id=app.job_id,
                first_name=app.first_name,
                last_name=app.last_name,
                email=app.email,
                cv_filename=app.cv_filename,
                cv_original_name=app.cv_original_name,
                cv_url=cv_url,
                created_at=app.created_at,
            )
        )
    return result


@router.get("/uploads/cv/{filename}")
def download_cv(filename: str):
    """Apertura e consultazione del curriculum vitae (R7)."""
    # Protezione base contro path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File del curriculum non trovato.",
        )

    # Restituisce il file PDF inline in modo che possa essere aperto e visualizzato
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_filename,
        content_disposition_type="inline",
    )
