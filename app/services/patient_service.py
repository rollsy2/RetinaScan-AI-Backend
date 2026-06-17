from app.repositories import patient_repository, scan_repository

def list_patients():
    return patient_repository.get_all_patients()

def get_patient_record(patient_id: int):
    try:
        patient = patient_repository.get_patient_by_id(patient_id)

        if not patient:
            return None

        return {
            "patient": patient,
            "scans": scan_repository.get_patient_scans(patient_id),
            "stats": scan_repository.get_patient_stats(patient_id)
        }

    except Exception as e:
        raise Exception(f"Service error: {str(e)}")
    
def create_patient(data):
    return patient_repository.create_patient(
        data.name,
        data.phone,
        data.age,
        data.gender,
        data.diagnosis,
        data.clinical_notes
    )

def update_patient(patient_id: int, data):
    fields = {}
    if data.diagnosis is not None:
        fields["diagnosis"] = data.diagnosis
    if data.clinical_notes is not None:
        fields["clinical_notes"] = data.clinical_notes
    if data.phone is not None:
        fields["phone"] = data.phone

    return patient_repository.update_patient(patient_id, fields)