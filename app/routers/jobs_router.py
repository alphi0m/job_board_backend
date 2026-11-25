from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Job, Company, Application
from ..schemas import JobCreate, JobOut, CompanyJobOut
from ..auth import get_current_company

router = APIRouter(tags=["Annunci di Lavoro"])


@router.get("/jobs", response_model=List[JobOut])
def get_all_jobs(db: Session = Depends(get_db)):
    """Consultazione bacheca pubblica (R5). Elenco di tutti gli annunci disponibili."""
    jobs = (
        db.query(Job, Company.name.label("company_name"))
        .join(Company, Job.company_id == Company.id)
        .order_by(Job.created_at.desc())
        .all()
    )
    result = []
    for job, company_name in jobs:
        result.append(
            JobOut(
                id=job.id,
                company_id=job.company_id,
                company_name=company_name,
                title=job.title,
                description=job.description,
                location=job.location,
                created_at=job.created_at,
            )
        )
    return result


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    """Consultazione dettaglio di un annuncio (R5)."""
    job_with_company = (
        db.query(Job, Company.name.label("company_name"))
        .join(Company, Job.company_id == Company.id)
        .filter(Job.id == job_id)
        .first()
    )
    if not job_with_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Annuncio non trovato.",
        )
    job, company_name = job_with_company
    return JobOut(
        id=job.id,
        company_id=job.company_id,
        company_name=company_name,
        title=job.title,
        description=job.description,
        location=job.location,
        created_at=job.created_at,
    )


@router.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    data: JobCreate,
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """Pubblicazione di un nuovo annuncio da parte di un'azienda autenticata (R4)."""
    if not data.title.strip() or not data.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Titolo e descrizione sono obbligatori.",
        )

    job = Job(
        company_id=current_company.id,
        title=data.title.strip(),
        description=data.description.strip(),
        location=data.location.strip() if data.location else "Remoto",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return JobOut(
        id=job.id,
        company_id=job.company_id,
        company_name=current_company.name,
        title=job.title,
        description=job.description,
        location=job.location,
        created_at=job.created_at,
    )


@router.get("/company/my-jobs", response_model=List[CompanyJobOut])
def get_my_jobs(
    current_company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """Elenco annunci pubblicati dall'azienda loggata con conteggio candidature (R7)."""
    # Query jobs of company and count applications
    jobs_with_count = (
        db.query(
            Job,
            func.count(Application.id).label("apps_count")
        )
        .outerjoin(Application, Job.id == Application.job_id)
        .filter(Job.company_id == current_company.id)
        .group_by(Job.id)
        .order_by(Job.created_at.desc())
        .all()
    )

    result = []
    for job, count in jobs_with_count:
        result.append(
            CompanyJobOut(
                id=job.id,
                company_id=job.company_id,
                company_name=current_company.name,
                title=job.title,
                description=job.description,
                location=job.location,
                created_at=job.created_at,
                applications_count=count,
            )
        )
    return result
