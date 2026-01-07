from typing import Generator
from sqlalchemy.orm import Session
from api.core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI pour obtenir une session de base de données.
    La session est automatiquement fermée après utilisation.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()