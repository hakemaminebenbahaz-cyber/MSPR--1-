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
