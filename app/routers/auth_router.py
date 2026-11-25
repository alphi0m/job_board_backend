from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Company
from ..schemas import CompanyRegister, CompanyLogin, CompanyOut, TokenOut
from ..auth import hash_password, verify_password, create_access_token, get_current_company

router = APIRouter(prefix="/auth", tags=["Autenticazione Azienda"])


@router.post("/register", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def register_company(data: CompanyRegister, db: Session = Depends(get_db)):
    """Registrazione nuovo account Azienda (R1)."""
    existing = db.query(Company).filter(Company.email == data.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un'azienda con questa email è già registrata.",
        )

    company = Company(
        name=data.name.strip(),
        email=data.email.lower().strip(),
        password_hash=hash_password(data.password),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.post("/login", response_model=TokenOut)
def login_company(data: CompanyLogin, db: Session = Depends(get_db)):
    """Login Azienda con rilascio del token JWT (R2)."""
    company = db.query(Company).filter(Company.email == data.email.lower().strip()).first()
    if not company or not verify_password(data.password, company.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali errate. Verifica email e password.",
        )

    access_token = create_access_token(data={"sub": str(company.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "company": company,
    }


@router.get("/me", response_model=CompanyOut)
def get_me(current_company: Company = Depends(get_current_company)):
    """Verifica sessione e restituisce i dati dell'azienda corrente."""
    return current_company


@router.post("/logout")
def logout_company(current_company: Company = Depends(get_current_company)):
    """Logout Azienda (R3)."""
    return {"message": "Logout effettuato con successo"}
