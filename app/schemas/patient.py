from pydantic import BaseModel
from typing import Optional


class PatientCreate(BaseModel):
    name: str
    phone: str
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = ""
    clinical_notes: Optional[str] = ""


class PatientUpdate(BaseModel):
    diagnosis: Optional[str] = None
    clinical_notes: Optional[str] = None
    phone: Optional[str] = None