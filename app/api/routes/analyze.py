from fastapi import APIRouter, File, UploadFile, Form
from app.services.analysis_service import analyze_files

router = APIRouter()

@router.post("/")
async def analyze(files: list[UploadFile] = File(...), patient_id: int = Form(None)):
    return {"results": analyze_files(files, patient_id)}