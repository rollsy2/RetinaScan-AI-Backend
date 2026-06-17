from app.database.init_db import init_db
from app.ai.model import load_model

def startup():
    init_db()
    load_model()