import io
from PIL import Image
from app.ai.model import run_analysis
from app.repositories.scan_repository import save_scan


def analyze_files(files, patient_id=None):
    results = []

    try:
        for file in files:
            raw = file.file.read()

            try:
                img = Image.open(io.BytesIO(raw))
            except Exception:
                raise ValueError(f"Invalid image: {file.filename}")

            result = run_analysis(img, file.filename)

            if patient_id:
                save_scan(
                    patient_id=patient_id,
                    filename=file.filename,
                    prediction=result["prediction"],
                    confidence=result["confidence"],
                    all_classes=result["all_classes"],
                    gradcam_base64=result["gradcam_base64"],
                    model_used=result["model_used"]
                )

            results.append(result)

        return results

    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")