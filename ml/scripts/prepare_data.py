"""
prepare_data.py — ObRail Europe
Chargement, nettoyage, encodage et séparation train/test des données ferroviaires.
Source : data/transformed/dessertes.csv (122 801 lignes)

Enjeux :
  1. Regression     — Predire la duree du trajet (duree_h)
  2. Classification — Predire si une liaison peut remplacer un vol court-courrier
  3. Clustering     — Identifier les familles de liaisons (K-Means, non-supervise)
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

RANDOM_STATE = 42
ROOT     = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_SRC = os.path.join(ROOT, "data", "transformed", "dessertes.csv")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")


# ── 1. Chargement ─────────────────────────────────────────────────────────────
def load():
    df = pd.read_csv(DATA_SRC, low_memory=False)
    print(f"Lignes chargees : {len(df):,}")
    return df


# ── 2. Nettoyage ──────────────────────────────────────────────────────────────
def clean(df):
    cols = ["type_ligne", "type_service", "duree_h",
            "distance_km", "emissions_co2_gkm", "frequence_hebdo", "traction"]
    df = df[cols].copy()

    for col in ["duree_h", "distance_km", "emissions_co2_gkm", "frequence_hebdo"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 59 valeurs manquantes frequence_hebdo -> mediane
    df["frequence_hebdo"] = df["frequence_hebdo"].fillna(df["frequence_hebdo"].median())

    avant = len(df)
    df.dropna(inplace=True)
    print(f"Lignes supprimees (corrompues) : {avant - len(df)}")
    print(f"Lignes restantes : {len(df):,}")
    return df


# ── 3. Encodage ───────────────────────────────────────────────────────────────
def encode(df):
    le_ligne   = LabelEncoder()
    le_service = LabelEncoder()

    df["type_ligne_enc"]   = le_ligne.fit_transform(df["type_ligne"])
    df["type_service_enc"] = le_service.fit_transform(df["type_service"])  # Jour=0, Nuit=1

    # traction_enc retire : 99.7% electrique, aucune variance utile
    print(f"Classes type_service : {dict(zip(le_service.classes_, le_service.transform(le_service.classes_)))}")
    print(f"Valeurs type_ligne   : {list(le_ligne.classes_)}")
    return df


# ── 4. Cible substituabilite avion->train ─────────────────────────────────────
def create_substituabilite(df):
    """
    Regle metier : une liaison est substituable a un vol court-courrier si :
      - distance >= 150 km    (trop court = pas de vol concurrentiel)
      - duree < 8 heures      (acceptable pour un professionnel en train)
      - frequence >= 2/semaine (service minimum viable)
    Note : seuil abaisse a 150km car notre dataset est majoritairement compose
    de trains regionaux courts (mediane 42km). Les trains 300km+ sont rares.
    """
    df["substituable"] = (
        (df["distance_km"] >= 150) &
        (df["duree_h"] < 8) &
        (df["frequence_hebdo"] >= 2)
    ).astype(int)

    nb_sub = df["substituable"].sum()
    total  = len(df)
    print(f"\nLiaisons substituables : {nb_sub:,} / {total:,} ({nb_sub/total*100:.1f}%)")
    print(f"Liaisons non substituables : {total - nb_sub:,} ({(total-nb_sub)/total*100:.1f}%)")
    return df


# ── 5. Separation train / test ────────────────────────────────────────────────
def split_and_save(df):
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- Regression : predire duree_h ---
    FEATURES_REG = ["distance_km", "type_ligne_enc", "type_service_enc",
                    "frequence_hebdo", "emissions_co2_gkm"]
    Xr_tr, Xr_te, yr_tr, yr_te = train_test_split(
        df[FEATURES_REG], df["duree_h"], test_size=0.2, random_state=RANDOM_STATE)

    # --- Classification : predire substituable (0/1) ---
    FEATURES_CLF = ["distance_km", "duree_h", "type_ligne_enc",
                    "frequence_hebdo", "emissions_co2_gkm"]
    Xc_tr, Xc_te, yc_tr, yc_te = train_test_split(
        df[FEATURES_CLF], df["substituable"],
        test_size=0.2, random_state=RANDOM_STATE, stratify=df["substituable"])

    # --- Clustering : toutes les features numeriques (non supervise) ---
    FEATURES_CLU = ["distance_km", "duree_h", "frequence_hebdo", "emissions_co2_gkm"]
    df[FEATURES_CLU].to_csv(f"{OUT_DIR}/X_cluster.csv", index=False)

    # Sauvegarde CSV regression
    Xr_tr.to_csv(f"{OUT_DIR}/X_reg_train.csv", index=False)
    Xr_te.to_csv(f"{OUT_DIR}/X_reg_test.csv",  index=False)
    yr_tr.to_csv(f"{OUT_DIR}/y_reg_train.csv",  index=False, header=True)
    yr_te.to_csv(f"{OUT_DIR}/y_reg_test.csv",   index=False, header=True)

    # Sauvegarde CSV classification
    Xc_tr.to_csv(f"{OUT_DIR}/X_clf_train.csv", index=False)
    Xc_te.to_csv(f"{OUT_DIR}/X_clf_test.csv",  index=False)
    yc_tr.to_csv(f"{OUT_DIR}/y_clf_train.csv",  index=False, header=True)
    yc_te.to_csv(f"{OUT_DIR}/y_clf_test.csv",   index=False, header=True)

    print(f"\n[Regression]     Train={len(Xr_tr):,}  Test={len(Xr_te):,}")
    print(f"[Classification] Train={len(Xc_tr):,}  Test={len(Xc_te):,}")
    print(f"[Clustering]     {len(df):,} lignes (non supervise, pas de split)")


# ── 6. Tableau des variables retenues (livrable 1) ────────────────────────────
def save_variable_table():
    rows = [
        {"Variable": "distance_km",       "Type": "Numerique",         "Description": "Distance en km entre les deux gares",                        "Utilisee pour": "Regression + Classification + Clustering"},
        {"Variable": "duree_h",           "Type": "Numerique",         "Description": "Duree du trajet en heures — CIBLE regression",               "Utilisee pour": "Classification + Clustering (feature)"},
        {"Variable": "frequence_hebdo",   "Type": "Numerique",         "Description": "Nombre de passages par semaine",                             "Utilisee pour": "Regression + Classification + Clustering"},
        {"Variable": "emissions_co2_gkm", "Type": "Numerique",         "Description": "Emissions CO2 en g/km (proxy type de train)",                "Utilisee pour": "Regression + Classification + Clustering"},
        {"Variable": "type_ligne_enc",    "Type": "Categoriel encode", "Description": "Grande vitesse=0 / Intercite=1 / Regional=2",               "Utilisee pour": "Regression + Classification"},
        {"Variable": "type_service_enc",  "Type": "Categoriel encode", "Description": "Jour=0 / Nuit=1",                                           "Utilisee pour": "Regression (feature)"},
        {"Variable": "substituable",      "Type": "Binaire cree",      "Description": "1=liaison remplace vol court-courrier, 0=non — CIBLE classif","Utilisee pour": "Classification (cible)"},
    ]
    tableau = pd.DataFrame(rows)
    tableau.to_csv(f"{OUT_DIR}/tableau_variables.csv", index=False)
    print(f"\nTableau des variables :")
    print(tableau.to_string(index=False))


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Preparation des donnees — ObRail Europe")
    print("=" * 55)

    df = load()
    df = clean(df)
    df = encode(df)
    df = create_substituabilite(df)

    print("\n--- Stats features numeriques ---")
    print(df[["distance_km", "duree_h", "frequence_hebdo", "emissions_co2_gkm"]].describe().round(2))

    split_and_save(df)
    save_variable_table()

    print("\n[OK] prepare_data.py termine - fichiers dans ml/data/")
