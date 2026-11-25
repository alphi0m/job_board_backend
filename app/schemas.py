from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Company Auth
class CompanyRegister(BaseModel):
    name: str
    email: str
    password: str


class CompanyLogin(BaseModel):
    email: str
    password: str


class CompanyOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    company: CompanyOut


# Job Offer
class JobCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = "Remoto"


class JobOut(BaseModel):
    id: int
    company_id: int
    company_name: str
    title: str
    description: str
    location: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyJobOut(JobOut):
    applications_count: int = 0


# Application
class ApplicationOut(BaseModel):
    id: int
    job_id: int
    first_name: str
    last_name: str
    email: str
    cv_filename: str
    cv_original_name: str
    cv_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationSuccess(BaseModel):
    message: str
    application_id: int
