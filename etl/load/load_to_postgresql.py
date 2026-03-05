# load_to_postgresql.py
# Charge les données transformées dans PostgreSQL Azure
import os
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL manquante dans le fichier .env")

engine = sqlalchemy.create_engine(DATABASE_URL)
TRANSFORMED_DIR = "data/transformed"


# ═══════════════════════════════════════════════════════════
# Connexion
# ═══════════════════════════════════════════════════════════

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connexion PostgreSQL OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False


# ═══════════════════════════════════════════════════════════
# 1. OPERATEURS
# ═══════════════════════════════════════════════════════════

def load_operateurs():
    print("\n── Chargement opérateurs ──")
    df = pd.read_csv(f"{TRANSFORMED_DIR}/operateurs.csv")

    # Colonnes pour la BDD (sans les colonnes internes _*)
    insert = df[["nom", "pays_code"]].drop_duplicates(subset=["nom"])

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE operateurs RESTART IDENTITY CASCADE"))
        insert.to_sql("operateurs", conn, if_exists="append", index=False)

    # Récupérer les IDs générés pour la jointure
    with engine.connect() as conn:
        db_ops = pd.read_sql("SELECT id, nom FROM operateurs", conn)

    print(f"  ✅ {len(db_ops)} opérateurs chargés")
    return db_ops


# ═══════════════════════════════════════════════════════════
# 2. GARES
# ═══════════════════════════════════════════════════════════

def load_gares():
    print("\n── Chargement gares ──")
    df = pd.read_csv(f"{TRANSFORMED_DIR}/gares.csv")

    insert = df[["nom", "pays_code", "latitude", "longitude"]].drop_duplicates(subset=["nom"])

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE gares RESTART IDENTITY CASCADE"))
        insert.to_sql("gares", conn, if_exists="append", index=False)

    with engine.connect() as conn:
        db_gares = pd.read_sql("SELECT id, nom FROM gares", conn)

    print(f"  ✅ {len(db_gares)} gares chargées")
    print(f"     Répartition pays :")
    pays = df.groupby("pays_code")["nom"].count()
    for p, n in pays.items():
        print(f"       {p} : {n}")
    return db_gares


# ═══════════════════════════════════════════════════════════
# 3. DESSERTES
# ═══════════════════════════════════════════════════════════

def load_dessertes(db_operateurs, db_gares):
    print("\n── Chargement dessertes ──")
    df = pd.read_csv(f"{TRANSFORMED_DIR}/dessertes.csv")

    # Résoudre FK operateur_id depuis le nom
    op_map  = dict(zip(db_operateurs["nom"], db_operateurs["id"]))
    df["operateur_id"] = df["operateur_nom"].map(op_map)

    # Résoudre FK gare_depart_id et gare_arrivee_id depuis le nom
    gare_map = dict(zip(db_gares["nom"], db_gares["id"]))
    df["gare_depart_id"]  = df["gare_depart_nom"].map(gare_map)
    df["gare_arrivee_id"] = df["gare_arrivee_nom"].map(gare_map)

    # Supprimer les lignes avec des FK manquantes
    avant = len(df)
    df = df.dropna(subset=["gare_depart_id", "gare_arrivee_id"])
    apres = len(df)
    if avant != apres:
        print(f"  ⚠️  {avant - apres} dessertes ignorées (gare introuvable)")

    # Colonnes finales pour la BDD
    insert = df[[
        "id", "operateur_id", "nom_ligne", "type_ligne", "type_service",
        "gare_depart_id", "gare_arrivee_id",
        "heure_depart", "heure_arrivee",
        "distance_km", "duree_h",
        "emissions_co2_gkm", "frequence_hebdo",
        "traction", "source_donnee",
    ]]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE dessertes"))
        insert.to_sql("dessertes", conn, if_exists="append", index=False)

    j = len(insert[insert["type_service"] == "Jour"])
    n = len(insert[insert["type_service"] == "Nuit"])
    print(f"  ✅ {len(insert)} dessertes chargées — Jour:{j} Nuit:{n}")
    return insert


# ═══════════════════════════════════════════════════════════
# PIPELINE LOAD
# ═══════════════════════════════════════════════════════════

def run_load_pipeline():
    print("=" * 60)
    print("LOAD — Chargement vers PostgreSQL Azure")
    print("=" * 60)

    if not test_connection():
        print("Abandon : connexion impossible.")
        return False

    # Vérifier que les fichiers transformés existent
    for f in ["operateurs.csv", "gares.csv", "dessertes.csv"]:
        if not os.path.exists(f"{TRANSFORMED_DIR}/{f}"):
            print(f"❌ Fichier manquant : {TRANSFORMED_DIR}/{f}")
            print("   Lance d'abord : python etl/transform/transform_gtfs.py")
            return False

    db_operateurs = load_operateurs()
    db_gares      = load_gares()
    load_dessertes(db_operateurs, db_gares)

    print("\n✅ Load terminé avec succès !")
    return True


if __name__ == "__main__":
    run_load_pipeline()
