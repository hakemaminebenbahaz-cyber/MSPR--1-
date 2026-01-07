from core.database import test_connection, SessionLocal
from core.config import settings
from sqlalchemy import text

def main():
    print(f"🔍 Tentative de connexion à : {settings.DATABASE_URL}")
    print("-" * 50)
    
    # Test de connexion
    if test_connection():
        print("\n✅ La connexion fonctionne!")
        
        # Essayer de lister les tables
        try:
            db = SessionLocal()
            result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            
            print("\n📊 Tables disponibles :")
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  Aucune table trouvée (schema 'public' vide)")
            
            db.close()
        except Exception as e:
            print(f"⚠️ Impossible de lister les tables : {e}")
    else:
        print("\n❌ La connexion a échoué!")
        print("👉 Vérifie ton fichier .env et que PostgreSQL est démarré")

if __name__ == "__main__":
    main()