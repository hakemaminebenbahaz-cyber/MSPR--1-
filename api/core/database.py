from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Créer l'engine de connexion
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Affiche les requêtes SQL dans la console (utile pour debug)
    pool_pre_ping=True  # Vérifie que la connexion est active avant de l'utiliser
)

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Fonction pour tester la connexion
def test_connection():
    try:
        with engine.connect() as connection:
            print("✅ Connexion à PostgreSQL réussie!")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False