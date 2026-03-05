# transform_gtfs.py
# Nettoie et fusionne plusieurs sources GTFS → operateurs.csv, gares.csv, dessertes.csv
import os
import re
import pandas as pd

RAW_DIR = "data/raw"
OUT_DIR = "data/transformed"
os.makedirs(OUT_DIR, exist_ok=True)

# Sources GTFS disponibles avec leur pays
GTFS_SOURCES = {
    "sncf_ter":   {"pays": "FR", "operateur_defaut": "SNCF",            "traction": "électrique", "co2": 14.0},
    "db_germany": {"pays": "DE", "operateur_defaut": "Deutsche Bahn",   "traction": "électrique", "co2": 32.0},
}


def read_gtfs(source, filename):
    path = os.path.join(RAW_DIR, source, filename)
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path, encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1", low_memory=False)


# ═══════════════════════════════════════════════════════════
# 1. OPERATEURS
# ═══════════════════════════════════════════════════════════

def transform_operateurs():
    print("\n── OPERATEURS ──")
    all_agencies = []

    for source, meta in GTFS_SOURCES.items():
        df = read_gtfs(source, "agency.txt")
        if df is None:
            print(f"  ⚠️  {source}/agency.txt introuvable")
            continue

        # Supprimer les faux opérateurs
        df = df[~df["agency_id"].astype(str).isin(["OCEdefault"])].copy()
        df["_source"] = source
        df["pays_code"] = meta["pays"]
        all_agencies.append(df)

    df_all = pd.concat(all_agencies, ignore_index=True)

    # Simplifier les agency_id trop longs (UUID)
    df_all["agency_id"] = df_all["agency_id"].apply(_simplify_agency_id)

    # Dédupliquer par nom d'opérateur
    df_all = df_all.drop_duplicates(subset=["agency_name"]).reset_index(drop=True)
    df_all.insert(0, "id", range(1, len(df_all) + 1))

    operateurs = df_all[["id", "agency_id", "agency_name", "pays_code", "_source"]].rename(
        columns={"agency_id": "_agency_id", "agency_name": "nom"}
    )

    operateurs.to_csv(f"{OUT_DIR}/operateurs.csv", index=False)
    print(f"  ✅ {len(operateurs)} opérateurs")
    for _, r in operateurs.iterrows():
        print(f"     [{r['pays_code']}] {r['nom']}")
    return operateurs


def _simplify_agency_id(aid):
    aid = str(aid)
    if aid.startswith("FR:Authority::"):
        return "REGION_ARA"
    return aid


# ═══════════════════════════════════════════════════════════
# 2. GARES
# ═══════════════════════════════════════════════════════════

def transform_gares():
    print("\n── GARES ──")
    all_stops = []

    for source, meta in GTFS_SOURCES.items():
        df = read_gtfs(source, "stops.txt")
        if df is None:
            print(f"  ⚠️  {source}/stops.txt introuvable")
            continue

        # Garder uniquement les StopArea (gares parentes)
        df = df[df["location_type"] == 1].copy()

        # Supprimer colonnes inutiles
        df = df.drop(columns=["stop_desc", "zone_id", "stop_url",
                               "parent_station", "location_type"], errors="ignore")

        df["stop_name"] = df["stop_name"].str.strip()
        df["pays_code"] = df.apply(
            lambda r: _detect_pays(r["stop_lat"], r["stop_lon"]), axis=1
        )
        df["_source"] = source
        all_stops.append(df)

    df_all = pd.concat(all_stops, ignore_index=True)

    # Dédupliquer par nom exact
    df_all = df_all.drop_duplicates(subset=["stop_name"]).reset_index(drop=True)
    df_all.insert(0, "id", range(1, len(df_all) + 1))

    # Normaliser les stop_ids en string (évite int vs float vs str)
    df_all["stop_id"] = df_all["stop_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    gares = df_all.rename(columns={
        "stop_name": "nom",
        "stop_lat":  "latitude",
        "stop_lon":  "longitude",
        "stop_id":   "_stop_id",
    })[["id", "nom", "pays_code", "latitude", "longitude", "_stop_id", "_source"]]

    gares.to_csv(f"{OUT_DIR}/gares.csv", index=False)
    print(f"  ✅ {len(gares)} gares")
    print(f"     Répartition : {gares['pays_code'].value_counts().to_dict()}")
    return gares


def _detect_pays(lat, lon):
    if 41.0 <= lat <= 51.5 and -5.5 <= lon <= 9.6:
        return "FR"
    if 47.0 <= lat <= 55.5 and 5.5 <= lon <= 15.5:
        return "DE"
    if 45.5 <= lat <= 48.0 and 5.5 <= lon <= 10.7:
        return "CH"
    if 35.5 <= lat <= 44.0 and -10.0 <= lon <= 4.5:
        return "ES"
    if 46.0 <= lat <= 49.0 and 9.5 <= lon <= 17.5:
        return "AT"
    if 49.5 <= lat <= 51.5 and 2.5 <= lon <= 6.5:
        return "BE"
    return "EU"


# ═══════════════════════════════════════════════════════════
# 3. DESSERTES
# ═══════════════════════════════════════════════════════════

def transform_dessertes(operateurs_df, gares_df):
    print("\n── DESSERTES ──")
    all_dessertes = []

    for source, meta in GTFS_SOURCES.items():
        print(f"\n  Traitement {source}...")

        routes = read_gtfs(source, "routes.txt")
        trips  = read_gtfs(source, "trips.txt")
        # Forcer trip_id et route_id en string pour éviter les type mismatch
        if trips is not None:
            trips["trip_id"]   = trips["trip_id"].astype(str).str.strip()
            trips["route_id"]  = trips["route_id"].astype(str).str.strip()
        if routes is not None:
            routes["route_id"] = routes["route_id"].astype(str).str.strip()
        stops  = read_gtfs(source, "stops.txt")
        st     = pd.read_csv(
            f"{RAW_DIR}/{source}/stop_times.txt", encoding="utf-8", low_memory=False,
            usecols=["trip_id", "departure_time", "arrival_time", "stop_id", "stop_sequence"],
            dtype={"stop_id": str, "trip_id": str}
        ) if os.path.exists(f"{RAW_DIR}/{source}/stop_times.txt") else None
        if st is not None:
            st["stop_id"] = st["stop_id"].str.strip().str.replace(r"\.0$", "", regex=True)

        if any(x is None for x in [routes, trips, stops, st]):
            print(f"  ⚠️  Fichiers manquants pour {source}, ignoré.")
            continue

        # Garder uniquement les trains (route_type=2)
        routes = routes[routes["route_type"] == 2].copy()
        routes = routes.drop(columns=["route_desc", "route_url", "route_color",
                                       "route_text_color"], errors="ignore")

        # Nettoyer trips
        if "direction_id" not in trips.columns:
            trips["direction_id"] = 0
        else:
            trips["direction_id"] = trips["direction_id"].fillna(0).astype(int)
        trips = trips.drop(columns=["shape_id"], errors="ignore")
        trips = trips[trips["route_id"].isin(routes["route_id"])]

        # Mapper StopPoint → StopArea (tout en string pour éviter les type mismatch int/str)
        stop_to_area = _build_stop_area_map(stops)
        area_to_nom  = {str(k): v for k, v in zip(gares_df["_stop_id"], gares_df["nom"])}
        area_to_id   = {str(k): v for k, v in zip(gares_df["_stop_id"], gares_df["id"])}

        # Premier et dernier arrêt par trip
        st_sorted = st.sort_values(["trip_id", "stop_sequence"])

        first = (st_sorted.groupby("trip_id", as_index=False).first()
                          [["trip_id", "departure_time", "stop_id"]]
                          .rename(columns={"stop_id": "stop_depart",
                                           "departure_time": "heure_depart"}))
        last  = (st_sorted.groupby("trip_id", as_index=False).last()
                          [["trip_id", "arrival_time", "stop_id"]]
                          .rename(columns={"stop_id": "stop_arrivee",
                                           "arrival_time": "heure_arrivee"}))

        # Forcer les clés de jointure en str juste avant le merge
        trips["trip_id"]   = trips["trip_id"].astype(str)
        trips["route_id"]  = trips["route_id"].astype(str)
        routes["route_id"] = routes["route_id"].astype(str)
        first["trip_id"]   = first["trip_id"].astype(str)
        last["trip_id"]    = last["trip_id"].astype(str)

        df = (trips
              .merge(first, on="trip_id")
              .merge(last,  on="trip_id")
              .merge(routes[["route_id", "agency_id", "route_short_name", "route_long_name"]],
                     on="route_id"))

        # Une desserte par (route, direction)
        df = df.drop_duplicates(subset=["route_id", "direction_id"]).reset_index(drop=True)

        rows = []
        for _, r in df.iterrows():
            area_dep = str(stop_to_area.get(r["stop_depart"], r["stop_depart"]))
            area_arr = str(stop_to_area.get(r["stop_arrivee"], r["stop_arrivee"]))

            nom_dep = area_to_nom.get(area_dep)
            nom_arr = area_to_nom.get(area_arr)
            id_dep  = area_to_id.get(area_dep)
            id_arr  = area_to_id.get(area_arr)

            if not nom_dep or not nom_arr or nom_dep == nom_arr:
                continue

            nom_ligne = _nom_ligne(r)
            rows.append({
                "id":               _make_id(source, r),
                "operateur_nom":    _get_operateur(operateurs_df, r["agency_id"]),
                "nom_ligne":        nom_ligne,
                "type_ligne":       _type_ligne(nom_ligne),
                "type_service":     _type_service(r["heure_depart"]),
                "gare_depart_nom":  nom_dep,
                "gare_depart_id":   id_dep,
                "gare_arrivee_nom": nom_arr,
                "gare_arrivee_id":  id_arr,
                "heure_depart":     _clean_time(r["heure_depart"]),
                "heure_arrivee":    _clean_time(r["heure_arrivee"]),
                "duree_h":          _duree(r["heure_depart"], r["heure_arrivee"]),
                "distance_km":      None,
                "emissions_co2_gkm": meta["co2"],
                "frequence_hebdo":  None,
                "traction":         meta["traction"],
                "source_donnee":    f"GTFS {source}",
            })

        if not rows:
            print(f"  ⚠️  Aucune desserte trouvée pour {source} (mapping gares vide)")
            # Debug : afficher quelques stop IDs du GTFS vs gares_df
            sample_stops = list(stop_to_area.values())[:5]
            sample_gares = list(area_to_id.keys())[:5]
            print(f"     Exemples stop_to_area values : {sample_stops}")
            print(f"     Exemples area_to_id keys     : {sample_gares}")
            continue

        source_df = pd.DataFrame(rows)
        all_dessertes.append(source_df)
        j = len(source_df[source_df["type_service"] == "Jour"])
        n = len(source_df[source_df["type_service"] == "Nuit"])
        print(f"  ✅ {len(source_df)} dessertes [{source}] — Jour:{j} Nuit:{n}")

    dessertes = pd.concat(all_dessertes, ignore_index=True)
    dessertes.to_csv(f"{OUT_DIR}/dessertes.csv", index=False)

    total_j = len(dessertes[dessertes["type_service"] == "Jour"])
    total_n = len(dessertes[dessertes["type_service"] == "Nuit"])
    print(f"\n  ✅ TOTAL : {len(dessertes)} dessertes — Jour:{total_j} Nuit:{total_n}")
    return dessertes


# ─── Utilitaires ────────────────────────────────────────────

def _build_stop_area_map(stops_df):
    """Construit StopPoint → StopArea, tout en string normalisé.
    Gère les cas SNCF (location_type=0/1) et DB (location_type=NaN avec parent_station).
    """
    def clean_id(v):
        s = str(v).strip()
        return s[:-2] if s.endswith(".0") else s

    m = {}
    for _, r in stops_df.iterrows():
        sid = clean_id(r["stop_id"])
        lt  = r.get("location_type")
        ps  = r.get("parent_station")

        is_area   = (str(lt).strip() in ("1", "1.0"))
        has_parent = pd.notna(ps) and str(ps).strip() not in ("", "nan")

        if is_area:
            # StopArea → mappe à lui-même
            m[sid] = sid
        elif has_parent:
            # StopPoint (location_type=0 ou NaN) avec parent → mappe vers le parent
            m[sid] = clean_id(ps)
        else:
            # Stop isolé sans parent → mappe à lui-même
            m[sid] = sid
    return m


def _get_operateur(operateurs_df, agency_id):
    agency_id = _simplify_agency_id(str(agency_id))
    match = operateurs_df[operateurs_df["_agency_id"].astype(str) == agency_id]
    return match.iloc[0]["nom"] if not match.empty else str(agency_id)


def _simplify_agency_id(aid):
    if str(aid).startswith("FR:Authority::"):
        return "REGION_ARA"
    return aid


def _clean_time(t):
    try:
        parts = str(t).split(":")
        h = int(parts[0]) % 24
        return f"{h:02d}:{parts[1]}:{parts[2]}"
    except Exception:
        return None


def _duree(dep, arr):
    try:
        def to_min(t):
            p = str(t).split(":")
            return int(p[0]) * 60 + int(p[1])
        d = to_min(arr) - to_min(dep)
        if d < 0:
            d += 1440
        return round(d / 60, 2)
    except Exception:
        return None


def _type_service(heure):
    try:
        h = int(str(heure).split(":")[0])
        return "Nuit" if h >= 22 or h < 4 else "Jour"
    except Exception:
        return "Jour"


def _type_ligne(nom):
    n = str(nom).lower()
    if "tgv" in n or "grande vitesse" in n or "ice" in n:
        return "Grande vitesse"
    if "intercit" in n or "intercity" in n or "ic " in n:
        return "Intercité"
    if "nuit" in n or "night" in n or "nacht" in n or "nightjet" in n:
        return "Train de nuit intern"
    return "Train régional"


def _nom_ligne(row):
    long  = str(row.get("route_long_name", "")).strip()
    short = str(row.get("route_short_name", "")).strip()
    if long and long.lower() not in ("nan", "none", ""):
        return long
    if short and short.lower() not in ("nan", "none", ""):
        return short
    return str(row.get("route_id", "?"))


def _make_id(source, row):
    prefix   = "FR" if source == "sncf_ter" else "DE"
    route_id = str(row.get("route_id", "X"))
    # Prendre les 8 derniers caractères alphanum du route_id pour l'unicité
    short    = re.sub(r"[^A-Za-z0-9]", "", route_id)[-8:]
    d        = int(row.get("direction_id", 0))
    return f"{prefix}_{short}_{d}"[:20]


# ═══════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("TRANSFORM — GTFS multi-sources → 3 tables")
    print("=" * 60)

    operateurs = transform_operateurs()
    gares      = transform_gares()
    dessertes  = transform_dessertes(operateurs, gares)

    print("\n" + "=" * 60)
    print("Fichiers générés dans data/transformed/ :")
    for f in ["operateurs.csv", "gares.csv", "dessertes.csv"]:
        path = f"{OUT_DIR}/{f}"
        if os.path.exists(path):
            size = os.path.getsize(path) // 1024
            print(f"  ✅ {f} ({size} Ko)")
    print("✅ Transform terminé !")
