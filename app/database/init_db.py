from app.database.connection import get_db

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            age INTEGER,
            gender TEXT,
            diagnosis TEXT DEFAULT '',
            clinical_notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            filename TEXT,
            prediction TEXT,
            confidence REAL,
            all_classes TEXT,
            gradcam_base64 TEXT,
            model_used TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    conn.commit()
    conn.close()