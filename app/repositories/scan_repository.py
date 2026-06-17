import json
from app.database.connection import get_db

def save_scan(patient_id, filename, prediction, confidence, all_classes, gradcam_base64, model_used):
    conn = get_db()

    conn.execute("""
        INSERT INTO scans (
            patient_id, filename, prediction,
            confidence, all_classes,
            gradcam_base64, model_used
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        filename,
        prediction,
        confidence,
        json.dumps(all_classes),
        gradcam_base64,
        model_used
    ))

    conn.commit()
    conn.close()

def get_patient_scans(patient_id: int):
    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM scans
        WHERE patient_id=?
        ORDER BY created_at DESC
    """, (patient_id,)).fetchall()

    conn.close()

    result = []

    for r in rows:
        s = dict(r)
        if s.get("all_classes"):
            try:
                s["all_classes"] = json.loads(s["all_classes"])
            except:
                pass
        result.append(s)

    return result

def get_patient_stats(patient_id: int):
    scans = get_patient_scans(patient_id)

    total = len(scans)
    normal = sum(1 for s in scans if s.get("prediction","").upper()=="NORMAL")

    return {
        "total_scans": total,
        "normal_scans": normal,
        "abnormal_scans": total - normal,
        "last_scan": scans[0]["created_at"] if scans else None
    }