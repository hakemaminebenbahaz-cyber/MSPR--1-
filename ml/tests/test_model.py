"""
Tests pytest — Modeles ML ObRail Europe
Verifie que les 3 modeles sont charges et produisent des predictions valides.

Usage :
  pytest ml/tests/test_model.py -v
  pytest ml/tests/test_model.py -v --tb=short
"""

import os
import pytest
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def models():
    """Charge les 3 modeles une seule fois pour tous les tests."""
    joblib = pytest.importorskip("joblib")
    reg_path = os.path.join(MODEL_DIR, "model_regression.pkl")
    clf_path = os.path.join(MODEL_DIR, "model_classification.pkl")
    clu_path = os.path.join(MODEL_DIR, "model_clustering.pkl")

    if not all(os.path.exists(p) for p in [reg_path, clf_path, clu_path]):
        pytest.skip("Modeles .pkl introuvables — lancez train.py d'abord")

    reg = joblib.load(reg_path)
    clf = joblib.load(clf_path)
    km, scaler = joblib.load(clu_path)
    return {"reg": reg, "clf": clf, "km": km, "scaler": scaler}


@pytest.fixture
def sample_reg():
    """Exemple Paris-Lyon : TGV, 450km, jour, freq 7, 14 g/km CO2."""
    return pd.DataFrame([{
        "distance_km": 450.0,
        "type_ligne_enc": 0,
        "type_service_enc": 0,
        "frequence_hebdo": 7.0,
        "emissions_co2_gkm": 14.0,
    }])


@pytest.fixture
def sample_clf():
    """Exemple Paris-Lyon pour classification."""
    return pd.DataFrame([{
        "distance_km": 450.0,
        "duree_h": 2.0,
        "type_ligne_enc": 0,
        "frequence_hebdo": 7.0,
        "emissions_co2_gkm": 14.0,
    }])


@pytest.fixture
def sample_clu():
    """Exemple clustering."""
    return pd.DataFrame([{
        "distance_km": 450.0,
        "duree_h": 2.0,
        "frequence_hebdo": 7.0,
        "emissions_co2_gkm": 14.0,
    }])


# ── Tests chargement ──────────────────────────────────────────────────────────

class TestChargementModeles:

    def test_modele_regression_charge(self, models):
        assert models["reg"] is not None

    def test_modele_classification_charge(self, models):
        assert models["clf"] is not None

    def test_modele_clustering_charge(self, models):
        assert models["km"] is not None
        assert models["scaler"] is not None

    def test_fichiers_pkl_existent(self):
        for nom in ["model_regression.pkl", "model_classification.pkl", "model_clustering.pkl"]:
            assert os.path.exists(os.path.join(MODEL_DIR, nom)), f"{nom} introuvable"


# ── Tests régression ───────────────────────────────────────────────────────────

class TestRegression:

    def test_prediction_retourne_un_float(self, models, sample_reg):
        pred = models["reg"].predict(sample_reg)[0]
        assert isinstance(float(pred), float)

    def test_prediction_positive(self, models, sample_reg):
        pred = models["reg"].predict(sample_reg)[0]
        assert pred > 0, "La durée prédite doit être positive"

    def test_prediction_inferieure_a_24h(self, models, sample_reg):
        pred = models["reg"].predict(sample_reg)[0]
        assert pred < 24, f"Durée prédite anormale : {pred}h"

    def test_train_regional_plus_court_que_tgv(self, models):
        """Un train régional de 50km doit être plus court qu'un TGV de 450km."""
        X_tgv = pd.DataFrame([{"distance_km": 450, "type_ligne_enc": 0,
                                "type_service_enc": 0, "frequence_hebdo": 7, "emissions_co2_gkm": 14}])
        X_reg = pd.DataFrame([{"distance_km": 50, "type_ligne_enc": 2,
                                "type_service_enc": 0, "frequence_hebdo": 7, "emissions_co2_gkm": 32}])
        pred_tgv = models["reg"].predict(X_tgv)[0]
        pred_reg = models["reg"].predict(X_reg)[0]
        assert pred_reg < pred_tgv, "Un trajet régional de 50km doit être plus court qu'un TGV de 450km"

    def test_distance_plus_grande_duree_plus_longue(self, models):
        """Plus la distance est grande, plus la durée doit être longue (toutes choses égales)."""
        X_court = pd.DataFrame([{"distance_km": 100, "type_ligne_enc": 1,
                                  "type_service_enc": 0, "frequence_hebdo": 5, "emissions_co2_gkm": 24}])
        X_long = pd.DataFrame([{"distance_km": 800, "type_ligne_enc": 1,
                                 "type_service_enc": 0, "frequence_hebdo": 5, "emissions_co2_gkm": 24}])
        assert models["reg"].predict(X_court)[0] < models["reg"].predict(X_long)[0]

    def test_batch_de_5_predictions(self, models):
        """Le modèle doit gérer plusieurs lignes en entrée."""
        X = pd.DataFrame([
            {"distance_km": 50,   "type_ligne_enc": 2, "type_service_enc": 0, "frequence_hebdo": 7, "emissions_co2_gkm": 32},
            {"distance_km": 200,  "type_ligne_enc": 1, "type_service_enc": 0, "frequence_hebdo": 5, "emissions_co2_gkm": 24},
            {"distance_km": 450,  "type_ligne_enc": 0, "type_service_enc": 0, "frequence_hebdo": 7, "emissions_co2_gkm": 14},
            {"distance_km": 800,  "type_ligne_enc": 1, "type_service_enc": 1, "frequence_hebdo": 3, "emissions_co2_gkm": 11},
            {"distance_km": 1200, "type_ligne_enc": 0, "type_service_enc": 0, "frequence_hebdo": 7, "emissions_co2_gkm": 14},
        ])
        preds = models["reg"].predict(X)
        assert len(preds) == 5
        assert all(p > 0 for p in preds)


# ── Tests classification ───────────────────────────────────────────────────────

class TestClassification:

    def test_prediction_binaire(self, models, sample_clf):
        pred = models["clf"].predict(sample_clf)[0]
        assert pred in [0, 1], f"Prediction invalide : {pred}"

    def test_probabilite_entre_0_et_1(self, models, sample_clf):
        proba = models["clf"].predict_proba(sample_clf)[0]
        assert len(proba) == 2
        assert 0.0 <= proba[0] <= 1.0
        assert 0.0 <= proba[1] <= 1.0
        assert abs(sum(proba) - 1.0) < 1e-6, "Les probabilités doivent sommer à 1"

    def test_liaison_courte_non_substituable(self, models):
        """Un train régional de 30km ne remplace pas un vol."""
        X = pd.DataFrame([{
            "distance_km": 30.0,
            "duree_h": 0.5,
            "type_ligne_enc": 2,
            "frequence_hebdo": 7.0,
            "emissions_co2_gkm": 32.0,
        }])
        pred = models["clf"].predict(X)[0]
        assert pred == 0, "Une liaison de 30km ne doit pas être substituable"

    def test_liaison_tgv_substituable(self, models):
        """Un TGV Paris-Lyon (450km, 2h, fréq 7) doit être substituable."""
        X = pd.DataFrame([{
            "distance_km": 450.0,
            "duree_h": 2.0,
            "type_ligne_enc": 0,
            "frequence_hebdo": 7.0,
            "emissions_co2_gkm": 14.0,
        }])
        pred = models["clf"].predict(X)[0]
        assert pred == 1, "Paris-Lyon TGV doit être substituable au vol"

    def test_liaison_trop_longue_non_substituable(self, models):
        """Un trajet de 15h dépasse le seuil de 8h → non substituable."""
        X = pd.DataFrame([{
            "distance_km": 2000.0,
            "duree_h": 15.0,
            "type_ligne_enc": 1,
            "frequence_hebdo": 2.0,
            "emissions_co2_gkm": 11.0,
        }])
        pred = models["clf"].predict(X)[0]
        assert pred == 0, "Un trajet de 15h ne doit pas être substituable"


# ── Tests clustering ───────────────────────────────────────────────────────────

class TestClustering:

    def test_prediction_cluster_valide(self, models, sample_clu):
        X_scaled = models["scaler"].transform(sample_clu)
        cluster = models["km"].predict(X_scaled)[0]
        assert 0 <= cluster <= 4, f"Cluster invalide : {cluster}"

    def test_scaler_normalise_correctement(self, models, sample_clu):
        X_scaled = models["scaler"].transform(sample_clu)
        assert X_scaled.shape == (1, 4), "Le scaler doit retourner 4 features"

    def test_nombre_de_clusters(self, models):
        assert models["km"].n_clusters == 5, "Le modele doit avoir 5 clusters"

    def test_train_regional_different_de_tgv(self, models):
        """Un train régional et un TGV doivent appartenir à des clusters différents."""
        X_local = pd.DataFrame([{"distance_km": 30, "duree_h": 0.5,
                                  "frequence_hebdo": 7, "emissions_co2_gkm": 32}])
        X_tgv = pd.DataFrame([{"distance_km": 800, "duree_h": 4.0,
                                "frequence_hebdo": 5, "emissions_co2_gkm": 14}])
        c1 = models["km"].predict(models["scaler"].transform(X_local))[0]
        c2 = models["km"].predict(models["scaler"].transform(X_tgv))[0]
        assert c1 != c2, "Trains très différents doivent etre dans des clusters différents"

    def test_predictions_reproductibles(self, models, sample_clu):
        """Deux appels identiques doivent retourner le même cluster."""
        X_scaled = models["scaler"].transform(sample_clu)
        c1 = models["km"].predict(X_scaled)[0]
        c2 = models["km"].predict(X_scaled)[0]
        assert c1 == c2
