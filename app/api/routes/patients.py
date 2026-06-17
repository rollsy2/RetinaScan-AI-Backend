from fastapi import APIRouter, HTTPException
from app.schemas.patient import PatientCreate, PatientUpdate
from app.services import patient_service
import sqlite3

router = APIRouter()

@router.get("/")
def all():
    return patient_service.list_patients()

@router.post("/")
def create(p: PatientCreate):
    try:
        return patient_service.create_patient(p)
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Phone exists")

@router.get("/{id}/record/")
def record(id: int):
    data = patient_service.get_patient_record(id)
    if not data:
        raise HTTPException(404)
    return data

@router.put("/{id}/")
def update(id: int, data: PatientUpdate):
    return patient_service.update_patient(id, data)