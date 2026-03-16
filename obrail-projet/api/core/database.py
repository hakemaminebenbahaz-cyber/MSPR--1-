from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
from core.config import settings

# Parser l'URL pour extraire les composants (gère le @ dans le mot de passe)
_url = urlparse(settings.DATABASE_URL)
_password = settings.DB_PASSWORD if settings.DB_PASSWORD else _url.password
engine = create_engine(
    URL.create(
        drivername="postgresql",
        username=_url.username,
        password=_password,
        host=_url.hostname,
        port=_url.port,
        database=_url.path.lstrip("/"),
        query={"sslmode": "require"},
    ),
    echo=True,
    pool_pre_ping=True
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