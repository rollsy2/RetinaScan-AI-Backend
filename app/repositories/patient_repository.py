import sqlite3
from app.database.connection import get_db


def get_all_patients():
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM patients").fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        raise RuntimeError(f"DB Error: {str(e)}")
    finally:
        conn.close()


def get_patient_by_id(patient_id: int):
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM patients WHERE id=?",
            (patient_id,)
        ).fetchone()
        return dict(row) if row else None
    except Exception as e:
        raise RuntimeError(f"DB Error: {str(e)}")
    finally:
        conn.close()


def create_patient(name, phone, age, gender, diagnosis, clinical_notes):
    try:
        conn = get_db()

        cur = conn.execute("""
            INSERT INTO patients (name, phone, age, gender, diagnosis, clinical_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, age, gender, diagnosis, clinical_notes))

        conn.commit()

        row = conn.execute(
            "SELECT * FROM patients WHERE id=?",
            (cur.lastrowid,)
        ).fetchone()

        return dict(row)

    finally:
        conn.close()


def update_patient(patient_id: int, fields: dict):
    try:
        conn = get_db()

        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [patient_id]

        conn.execute(
            f"UPDATE patients SET {set_clause} WHERE id=?",
            values
        )

        conn.commit()

        row = conn.execute(
            "SELECT * FROM patients WHERE id=?",
            (patient_id,)
        ).fetchone()

        return dict(row)

    except Exception as e:
        raise RuntimeError(f"DB Error: {str(e)}")
    finally:
        conn.close()
