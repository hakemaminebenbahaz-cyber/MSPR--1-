# transform_night_trains.py
# Transforme les trains de nuit (Open Night Train Database) pour les charger
# dans les tables operateurs / gares / dessertes de PostgreSQL
#
# Source: data/raw/opendata/night_trains_all.csv
# Sortie: data/transformed/night_trains_dessertes.csv
#         data/transformed/night_trains_gares.csv
#         data/transformed/night_trains_operateurs.csv

import sys
import os
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAW_FILE = "data/raw/opendata/night_trains_all.csv"
OUT_DIR  = "data/transformed"
os.makedirs(OUT_DIR, exist_ok=True)

# Noms complets des operateurs (agency_id -> nom lisible)
OPERATOR_NAMES = {
    "ATC":          "ATC Romania",
    "BDŽ":          "BDZ Bulgaria",
    "ČD":           "České dráhy",
    "CFR":          "CFR Calatori",
    "CFR/MÁV":      "CFR/MÁV",
    "CFR/MÁV/ÖBB":  "CFR/MÁV/ÖBB",
    "CFM/CFR":      "CFM/CFR",
    "CS":           "Caledonian Sleeper",
    "ES":           "Eurostar",
    "FS":           "Trenitalia",
    "GA":           "Great Anglia",
    "GWR":          "Great Western Railway",
    "HŽPP":         "HŽ Putnički prijevoz",
    "HŽPP/ÖBB":     "HŽPP/ÖBB",
    "MÁV":          "MÁV-Start",
    "NJ/SJ":        "Nightjet/SJ",
    "ÖBB":          "ÖBB Nightjet",
    "PKP":          "PKP Intercity",
    "RFI":          "RFI",
    "SNCF":         "SNCF",
    "SJ":           "SJ Sweden",
    "SZ":           "SŽ Slovenia",
    "TMR":          "TMR",
    "UZ":           "Ukrzaliznytsia",
    "VR":           "VR Finland",
    "WESTbahn":     "WESTbahn",
    "ZSR":          "ZSSK Slovakia",
}

# Pays principal par agency_id (pour les gares sans info pays)
OPERATOR_COUNTRY = {
    "ATC": "RO", "BDŽ": "BG", "ČD": "CZ", "CFR": "RO",
    "CS":  "GB", "ES":  "GB", "FS": "IT", "GA":  "GB",
    "GWR": "GB", "HŽPP": "HR", "MÁV": "HU", "ÖBB": "AT",
    "PKP": "PL", "SNCF": "FR", "SJ": "SE", "SZ": "SI",
    "UZ":  "UA", "VR":  "FI", "ZSR": "SK",
}


def parse_duration(val):
    """Convertit 'HH:MM:SS' en float heures. Retourne None si invalide."""
    try:
        parts = str(val).strip().split(":")
        if len(parts) >= 2:
            return round(int(parts[0]) + int(parts[1]) / 60, 2)
    except Exception:
        pass
    return None


def transform():
    print("=" * 60)
    print("TRANSFORM — Trains de nuit (Open Night Train Database)")
    print("=" * 60)

    df = pd.read_csv(RAW_FILE)
    print(f"  Lu: {len(df)} lignes")

    # Garder actifs uniquement
    df = df[df["is_active"].str.strip().str.upper() == "Y"].copy()
    print(f"  Actifs: {len(df)} lignes")

    # ─── OPERATEURS ───────────────────────────────────────────
    agencies = df["agency_id"].dropna().unique()
    ops_rows = []
    for ag in agencies:
        ag = ag.strip()
        pays = OPERATOR_COUNTRY.get(ag, "EU")
        # Si plusieurs pays dans l'agency_id (ex: "CFR/MÁV"), prendre le 1er
        for part in ag.split("/"):
            pays = OPERATOR_COUNTRY.get(part.strip(), pays)
            break
        ops_rows.append({
            "nom":       OPERATOR_NAMES.get(ag, ag),
            "pays_code": pays,
            "_agency_id": ag,
        })

    df_ops = pd.DataFrame(ops_rows).drop_duplicates(subset=["nom"])
    ops_path = f"{OUT_DIR}/night_trains_operateurs.csv"
    df_ops.to_csv(ops_path, index=False, encoding="utf-8")
    print(f"\n  ✅ {len(df_ops)} operateurs → {ops_path}")

    # ─── GARES ────────────────────────────────────────────────
    # On extrait les noms de gare depuis trip_origin et trip_headsign
    # On utilise le pays du trajet (colonne 'countries', parfois multi)
    gare_depart  = df[["trip_origin",   "countries", "agency_id"]].rename(columns={"trip_origin":   "nom"})
    gare_arrivee = df[["trip_headsign", "countries", "agency_id"]].rename(columns={"trip_headsign": "nom"})

    gares_raw = pd.concat([gare_depart, gare_arrivee], ignore_index=True)
    gares_raw["nom"] = gares_raw["nom"].str.strip()

    # pays_code = premier pays listé dans countries
    gares_raw["pays_code"] = gares_raw["countries"].fillna("").str.split(",").str[0].str.strip()
    gares_raw.loc[gares_raw["pays_code"] == "", "pays_code"] = \
        gares_raw.loc[gares_raw["pays_code"] == "", "agency_id"].map(OPERATOR_COUNTRY).fillna("EU")

    df_gares = (
        gares_raw[["nom", "pays_code"]]
        .drop_duplicates(subset=["nom"])
        .reset_index(drop=True)
    )
    # Pas de coordonnées GPS pour ces gares (données non disponibles dans la source)
    df_gares["latitude"]  = None
    df_gares["longitude"] = None

    gares_path = f"{OUT_DIR}/night_trains_gares.csv"
    df_gares.to_csv(gares_path, index=False, encoding="utf-8")
    print(f"  ✅ {len(df_gares)} gares → {gares_path}")

    # ─── DESSERTES ────────────────────────────────────────────
    df["duree_h"]    = df["duration"].apply(parse_duration)
    df["distance_km"] = pd.to_numeric(df["distance"], errors="coerce")
    df["emissions_co2_gkm"] = pd.to_numeric(df["co2_per_km"], errors="coerce")
    df["operateur_nom"] = df["agency_id"].str.strip().map(
        lambda ag: OPERATOR_NAMES.get(ag, ag)
    )
    df["gare_depart_nom"]  = df["trip_origin"].str.strip()
    df["gare_arrivee_nom"] = df["trip_headsign"].str.strip()
    df["type_service"] = "Nuit"
    df["type_ligne"]   = "Train de nuit"
    df["traction"]     = "Electrique"
    df["frequence_hebdo"] = 7  # quotidien (is_active=Y sans précision)
    df["source_donnee"]   = "Open Night Train Database (Back-on-Track)"
    df["nom_ligne"]       = df["trip_short_name"].fillna(df["agency_id"] + " night train")
    df["heure_depart"]    = df["origin_departure_time"]
    df["heure_arrivee"]   = df["destination_arrival_time"]

    df_dessertes = df[[
        "operateur_nom", "nom_ligne", "type_ligne", "type_service",
        "gare_depart_nom", "gare_arrivee_nom",
        "heure_depart", "heure_arrivee",
        "distance_km", "duree_h",
        "emissions_co2_gkm", "frequence_hebdo",
        "traction", "source_donnee"
    ]].copy()

    dessertes_path = f"{OUT_DIR}/night_trains_dessertes.csv"
    df_dessertes.to_csv(dessertes_path, index=False, encoding="utf-8")
    print(f"  ✅ {len(df_dessertes)} dessertes → {dessertes_path}")

    print("\n" + "=" * 60)
    print("✅ TRANSFORM TERMINE")
    print("=" * 60)
    print(f"\nProchaine etape: python etl/load/load_to_postgresql.py")

    return df_ops, df_gares, df_dessertes


if __name__ == "__main__":
    transform()
