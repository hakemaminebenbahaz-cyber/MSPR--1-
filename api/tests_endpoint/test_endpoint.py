"""
Tests des endpoints de l'API ObRail Europe.
Lancer avec : pytest api/tests_endpoint/test_endpoint.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

API_KEY = "obrail-api-key-2026"
AUTH = {"X-API-Key": API_KEY}

client = TestClient(app)


# ═══════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "ObRail" in r.json()["message"]

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


# ═══════════════════════════════════════════════════════════
# OPERATEURS
# ═══════════════════════════════════════════════════════════

def test_get_operateurs():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "nom" in data[0]
    assert "pays_code" in data[0]

def test_get_operateurs_filtre_pays():
    r = client.get("/api/v1/operateurs/?pays_code=FR", headers=AUTH)
    assert r.status_code == 200
    for op in r.json():
        assert op["pays_code"] == "FR"

def test_get_operateur_by_id():
    r = client.get("/api/v1/operateurs/1", headers=AUTH)
    assert r.status_code == 200
    assert "nom" in r.json()

def test_get_operateur_inexistant():
    r = client.get("/api/v1/operateurs/99999", headers=AUTH)
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════
# GARES
# ═══════════════════════════════════════════════════════════

def test_get_gares():
    r = client.get("/api/v1/gares/", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "nom" in data[0]
    assert "latitude" in data[0]

def test_get_gares_filtre_pays():
    r = client.get("/api/v1/gares/?pays_code=FR&limit=10", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        assert g["pays_code"] == "FR"

def test_get_gares_recherche_nom():
    r = client.get("/api/v1/gares/?nom=Paris&limit=10", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        assert "paris" in g["nom"].lower()

def test_get_gare_by_id():
    r = client.get("/api/v1/gares/1", headers=AUTH)
    assert r.status_code == 200
    assert "nom" in r.json()

def test_get_gare_inexistante():
    r = client.get("/api/v1/gares/99999", headers=AUTH)
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════
# DESSERTES
# ═══════════════════════════════════════════════════════════

def test_get_dessertes():
    r = client.get("/api/v1/dessertes/?limit=10", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "nom_ligne" in data[0]
    assert "type_service" in data[0]

def test_get_dessertes_filtre_jour():
    r = client.get("/api/v1/dessertes/?type_service=Jour&limit=10", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["type_service"] == "Jour"

def test_get_dessertes_filtre_nuit():
    r = client.get("/api/v1/dessertes/?type_service=Nuit&limit=10", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["type_service"] == "Nuit"

def test_get_dessertes_recherche_depart():
    r = client.get("/api/v1/dessertes/?depart=Paris&limit=10", headers=AUTH)
    assert r.status_code == 200

def test_get_dessertes_recherche_arrivee():
    r = client.get("/api/v1/dessertes/?arrivee=Lyon&limit=10", headers=AUTH)
    assert r.status_code == 200

def test_get_desserte_by_id():
    # Récupère d'abord une ID valide
    r = client.get("/api/v1/dessertes/?limit=1", headers=AUTH)
    assert r.status_code == 200
    desserte_id = r.json()[0]["id"]
    r2 = client.get(f"/api/v1/dessertes/{desserte_id}", headers=AUTH)
    assert r2.status_code == 200
    assert r2.json()["id"] == desserte_id

def test_get_desserte_inexistante():
    r = client.get("/api/v1/dessertes/INVALID_ID_XYZ", headers=AUTH)
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════
# COMPARISONS
# ═══════════════════════════════════════════════════════════

def test_stats_globales():
    r = client.get("/api/v1/comparisons/stats-globales", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "total_dessertes" in data
    assert "total_gares" in data
    assert "total_operateurs" in data
    assert data["total_dessertes"] > 0

def test_jour_vs_nuit():
    r = client.get("/api/v1/comparisons/jour-vs-nuit", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    types = [d["type_service"] for d in data]
    assert "Jour" in types
    assert "Nuit" in types

def test_par_type_ligne():
    r = client.get("/api/v1/comparisons/par-type-ligne", headers=AUTH)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_par_pays():
    r = client.get("/api/v1/comparisons/par-pays", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    pays_codes = [d["pays_code"] for d in data]
    assert "FR" in pays_codes

def test_par_operateur():
    r = client.get("/api/v1/comparisons/par-operateur", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "operateur" in data[0]
    assert "nb_jour" in data[0]
    assert "nb_nuit" in data[0]


# ═══════════════════════════════════════════════════════════
# SECURITE — API KEY
# ═══════════════════════════════════════════════════════════

def test_sans_api_key_retourne_401():
    r = client.get("/api/v1/gares/")
    assert r.status_code == 401

def test_mauvaise_api_key_retourne_401():
    r = client.get("/api/v1/gares/", headers={"X-API-Key": "mauvaise-cle"})
    assert r.status_code == 401

def test_health_sans_api_key():
    """Le endpoint /health doit rester public."""
    r = client.get("/health")
    assert r.status_code == 200

def test_root_sans_api_key():
    """Le endpoint / doit rester public."""
    r = client.get("/")
    assert r.status_code == 200


# ═══════════════════════════════════════════════════════════
# OPERATEURS — tests complémentaires
# ═══════════════════════════════════════════════════════════

def test_get_operateurs_filtre_pays_de():
    r = client.get("/api/v1/operateurs/?pays_code=DE", headers=AUTH)
    assert r.status_code == 200
    for op in r.json():
        assert op["pays_code"] == "DE"

def test_get_operateurs_pays_inexistant_retourne_liste_vide():
    r = client.get("/api/v1/operateurs/?pays_code=ZZ", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == []

def test_get_operateurs_champs_complets():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    op = r.json()[0]
    assert "id" in op
    assert "nom" in op
    assert "pays_code" in op

def test_get_operateurs_retourne_plusieurs_pays():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    pays = {op["pays_code"] for op in r.json()}
    assert len(pays) > 1


# ═══════════════════════════════════════════════════════════
# GARES — tests complémentaires
# ═══════════════════════════════════════════════════════════

def test_get_gares_limit():
    r = client.get("/api/v1/gares/?limit=3", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()) <= 3

def test_get_gares_limit_1():
    r = client.get("/api/v1/gares/?limit=1", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_get_gares_coordonnees_gps():
    r = client.get("/api/v1/gares/?limit=10", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        assert "latitude" in g
        assert "longitude" in g

def test_get_gares_filtre_pays_de():
    r = client.get("/api/v1/gares/?pays_code=DE&limit=10", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        assert g["pays_code"] == "DE"

def test_get_gares_recherche_nom_insensible_casse():
    r = client.get("/api/v1/gares/?nom=paris&limit=10", headers=AUTH)
    assert r.status_code == 200

def test_get_gares_champs_complets():
    r = client.get("/api/v1/gares/?limit=1", headers=AUTH)
    assert r.status_code == 200
    g = r.json()[0]
    assert "id" in g
    assert "nom" in g
    assert "pays_code" in g

def test_get_gares_nom_inexistant_retourne_liste_vide():
    r = client.get("/api/v1/gares/?nom=XYZXYZXYZ", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == []


# ═══════════════════════════════════════════════════════════
# DESSERTES — tests complémentaires
# ═══════════════════════════════════════════════════════════

def test_get_dessertes_limit():
    r = client.get("/api/v1/dessertes/?limit=5", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()) <= 5

def test_get_dessertes_filtre_combine_jour_et_depart():
    r = client.get("/api/v1/dessertes/?type_service=Jour&depart=Paris&limit=10", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["type_service"] == "Jour"

def test_get_dessertes_filtre_combine_nuit_et_arrivee():
    r = client.get("/api/v1/dessertes/?type_service=Nuit&arrivee=Paris&limit=10", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["type_service"] == "Nuit"

def test_get_dessertes_champs_complets():
    r = client.get("/api/v1/dessertes/?limit=1", headers=AUTH)
    assert r.status_code == 200
    d = r.json()[0]
    assert "id" in d
    assert "nom_ligne" in d
    assert "type_service" in d

def test_get_dessertes_type_service_valeurs():
    r = client.get("/api/v1/dessertes/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["type_service"] in ["Jour", "Nuit"]

def test_get_dessertes_filtre_type_ligne_grande_vitesse():
    r = client.get("/api/v1/dessertes/?type_ligne=Grande vitesse&limit=10", headers=AUTH)
    assert r.status_code == 200

def test_get_dessertes_sans_filtre_retourne_resultats():
    r = client.get("/api/v1/dessertes/", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()) > 0


# ═══════════════════════════════════════════════════════════
# COMPARISONS — tests complémentaires
# ═══════════════════════════════════════════════════════════

def test_stats_globales_coherence():
    r = client.get("/api/v1/comparisons/stats-globales", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["total_operateurs"] > 0
    assert data["total_gares"] > 0
    assert data["total_dessertes"] > 0
    assert data["total_jour"] + data["total_nuit"] == data["total_dessertes"]

def test_stats_globales_champs_presents():
    r = client.get("/api/v1/comparisons/stats-globales", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    for champ in ["total_operateurs", "total_gares", "total_dessertes", "total_jour", "total_nuit"]:
        assert champ in data

def test_jour_vs_nuit_deux_types_exactement():
    r = client.get("/api/v1/comparisons/jour-vs-nuit", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    types = [d["type_service"] for d in data]
    assert "Jour" in types
    assert "Nuit" in types

def test_jour_vs_nuit_champs_co2():
    r = client.get("/api/v1/comparisons/jour-vs-nuit", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert "co2_moyen" in d
        assert "duree_moyenne_h" in d

def test_par_type_ligne_retourne_types():
    r = client.get("/api/v1/comparisons/par-type-ligne", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert "type_ligne" in data[0]
    assert "total" in data[0]

def test_par_pays_contient_fr_et_de():
    r = client.get("/api/v1/comparisons/par-pays", headers=AUTH)
    assert r.status_code == 200
    pays_codes = [d["pays_code"] for d in r.json()]
    assert "FR" in pays_codes
    assert "DE" in pays_codes

def test_par_pays_champs_complets():
    r = client.get("/api/v1/comparisons/par-pays", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert "pays_code" in d
        assert "total_dessertes" in d

def test_par_operateur_totaux_coherents():
    r = client.get("/api/v1/comparisons/par-operateur", headers=AUTH)
    assert r.status_code == 200
    for op in r.json():
        assert op["nb_jour"] + op["nb_nuit"] == op["total_dessertes"]

def test_inter_pays_retourne_liaisons():
    r = client.get("/api/v1/comparisons/inter-pays", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "liaison" in data[0]
        assert "gare_depart" in data[0]
        assert "gare_arrivee" in data[0]

def test_qualite_donnees_retourne_champs():
    r = client.get("/api/v1/comparisons/qualite-donnees", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "table" in data[0]
        assert "taux_completude" in data[0]

def test_qualite_donnees_taux_entre_0_et_100():
    r = client.get("/api/v1/comparisons/qualite-donnees", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert 0 <= d["taux_completude"] <= 100

def test_contexte_pays_retourne_donnees():
    r = client.get("/api/v1/comparisons/contexte-pays", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "pays_code" in data[0]


# ═══════════════════════════════════════════════════════════
# SECURITE — tests complémentaires
# ═══════════════════════════════════════════════════════════

def test_tous_les_endpoints_v1_sans_cle_retournent_401():
    endpoints = [
        "/api/v1/operateurs/",
        "/api/v1/gares/",
        "/api/v1/dessertes/",
        "/api/v1/comparisons/stats-globales",
        "/api/v1/comparisons/jour-vs-nuit",
        "/api/v1/comparisons/par-pays",
    ]
    for endpoint in endpoints:
        r = client.get(endpoint)
        assert r.status_code == 401, f"Attendu 401 sur {endpoint}, obtenu {r.status_code}"

def test_cle_vide_retourne_401():
    r = client.get("/api/v1/gares/", headers={"X-API-Key": ""})
    assert r.status_code == 401

def test_reponse_401_contient_message():
    r = client.get("/api/v1/gares/")
    assert r.status_code == 401
    assert "detail" in r.json()

def test_docs_sans_api_key():
    r = client.get("/docs")
    assert r.status_code == 200

def test_metrics_sans_api_key():
    r = client.get("/metrics")
    assert r.status_code == 200


# ═══════════════════════════════════════════════════════════
# OPERATEURS — validation des données
# ═══════════════════════════════════════════════════════════

def test_operateurs_nom_jamais_vide():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    for op in r.json():
        assert op["nom"] is not None
        assert op["nom"].strip() != ""

def test_operateurs_pays_code_deux_caracteres():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    for op in r.json():
        assert len(op["pays_code"]) == 2

def test_operateurs_id_entier_positif():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    for op in r.json():
        assert isinstance(op["id"], int)
        assert op["id"] > 0

def test_operateur_detail_coherent_avec_liste():
    r = client.get("/api/v1/operateurs/", headers=AUTH)
    assert r.status_code == 200
    premier = r.json()[0]
    r2 = client.get(f"/api/v1/operateurs/{premier['id']}", headers=AUTH)
    assert r2.status_code == 200
    assert r2.json()["id"] == premier["id"]
    assert r2.json()["nom"] == premier["nom"]


# ═══════════════════════════════════════════════════════════
# GARES — validation des données
# ═══════════════════════════════════════════════════════════

def test_gares_coordonnees_latitude_realiste():
    r = client.get("/api/v1/gares/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        if g["latitude"] is not None:
            assert -90 <= float(g["latitude"]) <= 90

def test_gares_coordonnees_longitude_realiste():
    r = client.get("/api/v1/gares/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        if g["longitude"] is not None:
            assert -180 <= float(g["longitude"]) <= 180

def test_gares_nom_jamais_vide():
    r = client.get("/api/v1/gares/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        assert g["nom"] is not None
        assert g["nom"].strip() != ""

def test_gares_id_entier_positif():
    r = client.get("/api/v1/gares/?limit=10", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        assert isinstance(g["id"], int)
        assert g["id"] > 0

def test_gares_pays_code_deux_caracteres():
    r = client.get("/api/v1/gares/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for g in r.json():
        if g["pays_code"] is not None:
            assert len(g["pays_code"]) == 2

def test_gares_limit_respecte():
    for limit in [1, 5, 10]:
        r = client.get(f"/api/v1/gares/?limit={limit}", headers=AUTH)
        assert r.status_code == 200
        assert len(r.json()) <= limit

def test_gare_detail_coherent_avec_liste():
    r = client.get("/api/v1/gares/?limit=1", headers=AUTH)
    assert r.status_code == 200
    premiere = r.json()[0]
    r2 = client.get(f"/api/v1/gares/{premiere['id']}", headers=AUTH)
    assert r2.status_code == 200
    assert r2.json()["nom"] == premiere["nom"]


# ═══════════════════════════════════════════════════════════
# DESSERTES — validation des données
# ═══════════════════════════════════════════════════════════

def test_dessertes_filtre_depart_et_arrivee_combines():
    r = client.get("/api/v1/dessertes/?depart=Paris&arrivee=Lyon&limit=10", headers=AUTH)
    assert r.status_code == 200

def test_dessertes_duree_positive_si_renseignee():
    r = client.get("/api/v1/dessertes/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        if d.get("duree_h") is not None:
            assert float(d["duree_h"]) > 0

def test_dessertes_co2_positif_si_renseigne():
    r = client.get("/api/v1/dessertes/?limit=50", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        if d.get("emissions_co2_gkm") is not None:
            assert float(d["emissions_co2_gkm"]) > 0

def test_dessertes_filtre_triple_combine():
    r = client.get("/api/v1/dessertes/?depart=Paris&type_service=Jour&type_ligne=Grande vitesse&limit=10", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["type_service"] == "Jour"

def test_dessertes_limit_respecte():
    for limit in [1, 5, 10]:
        r = client.get(f"/api/v1/dessertes/?limit={limit}", headers=AUTH)
        assert r.status_code == 200
        assert len(r.json()) <= limit

def test_dessertes_nom_ligne_jamais_vide():
    r = client.get("/api/v1/dessertes/?limit=20", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["nom_ligne"] is not None
        assert d["nom_ligne"].strip() != ""


# ═══════════════════════════════════════════════════════════
# COMPARISONS — cohérence croisée des données
# ═══════════════════════════════════════════════════════════

def test_stats_globales_coherence_avec_par_pays():
    stats = client.get("/api/v1/comparisons/stats-globales", headers=AUTH).json()
    par_pays = client.get("/api/v1/comparisons/par-pays", headers=AUTH).json()
    total_par_pays = sum(p["total_dessertes"] for p in par_pays)
    assert total_par_pays <= stats["total_dessertes"]

def test_par_operateur_trie_par_volume_decroissant():
    r = client.get("/api/v1/comparisons/par-operateur", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    totaux = [d["total_dessertes"] for d in data]
    assert totaux == sorted(totaux, reverse=True)

def test_inter_pays_liaisons_entre_pays_differents():
    r = client.get("/api/v1/comparisons/inter-pays", headers=AUTH)
    assert r.status_code == 200
    for liaison in r.json():
        pays = liaison["liaison"].split("-")
        if len(pays) == 2:
            assert pays[0].strip() != pays[1].strip()

def test_qualite_donnees_toutes_les_tables_presentes():
    r = client.get("/api/v1/comparisons/qualite-donnees", headers=AUTH)
    assert r.status_code == 200
    tables = {d["table"] for d in r.json()}
    assert "operateurs" in tables
    assert "gares" in tables
    assert "dessertes" in tables

def test_qualite_donnees_remplis_plus_petit_que_total():
    r = client.get("/api/v1/comparisons/qualite-donnees", headers=AUTH)
    assert r.status_code == 200
    for d in r.json():
        assert d["remplis"] <= d["total"]
        assert d["manquants"] == d["total"] - d["remplis"]

def test_jour_vs_nuit_totaux_coherents_avec_stats():
    stats = client.get("/api/v1/comparisons/stats-globales", headers=AUTH).json()
    jn = client.get("/api/v1/comparisons/jour-vs-nuit", headers=AUTH).json()
    total_jn = sum(d["total"] for d in jn)
    assert total_jn == stats["total_dessertes"]


# ═══════════════════════════════════════════════════════════
# FORMAT DES RÉPONSES — headers et content-type
# ═══════════════════════════════════════════════════════════

def test_reponse_json_content_type():
    endpoints = [
        "/api/v1/operateurs/",
        "/api/v1/gares/",
        "/api/v1/dessertes/",
        "/api/v1/comparisons/stats-globales",
    ]
    for endpoint in endpoints:
        r = client.get(endpoint, headers=AUTH)
        assert "application/json" in r.headers.get("content-type", ""), \
            f"Content-Type incorrect sur {endpoint}"

def test_reponse_401_est_json_pas_html():
    r = client.get("/api/v1/gares/")
    assert r.status_code == 401
    assert "application/json" in r.headers.get("content-type", "")
    data = r.json()
    assert isinstance(data, dict)
    assert "detail" in data

def test_health_retourne_service_obrail():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "service" in data
    assert "ObRail" in data["service"]

def test_root_retourne_tous_les_endpoints():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "endpoints" in data
    endpoints = data["endpoints"]
    assert "operateurs" in endpoints
    assert "gares" in endpoints
    assert "dessertes" in endpoints
    assert "comparisons" in endpoints
