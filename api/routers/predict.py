"""
Endpoint /predict — ObRail Europe
Expose les 3 modeles ML via l'API REST.
Les modeles .pkl sont charges une seule fois au demarrage (lifespan).
"""

import os
import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")

_models: dict = {}


def get_models() -> dict:
    if not _models:
        try:
            _models["reg"] = joblib.load(os.path.join(MODEL_DIR, "model_regression.pkl"))
            _models["clf"] = joblib.load(os.path.join(MODEL_DIR, "model_classification.pkl"))
            km, scaler = joblib.load(os.path.join(MODEL_DIR, "model_clustering.pkl"))
            _models["km"] = km
            _models["scaler"] = scaler
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Modeles ML non disponibles. Lancez train.py d'abord. ({e})"
            )
    return _models


# ── Schemas ────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    distance_km: float = Field(..., gt=0, example=450.0, description="Distance en km entre les deux gares")
    type_ligne: int = Field(..., ge=0, le=2, example=0, description="0=Grande vitesse, 1=Intercité, 2=Régional")
    type_service: int = Field(0, ge=0, le=1, example=0, description="0=Jour, 1=Nuit")
    frequence_hebdo: float = Field(..., gt=0, le=7, example=7.0, description="Passages par semaine")
    emissions_co2_gkm: float = Field(..., gt=0, example=14.0, description="Emissions CO2 en g/km")
    duree_h: float | None = Field(None, example=2.0, description="Durée réelle (optionnel — sinon prédite)")

    class Config:
        json_schema_extra = {
            "example": {
                "distance_km": 450,
                "type_ligne": 0,
                "type_service": 0,
                "frequence_hebdo": 7,
                "emissions_co2_gkm": 14,
                "duree_h": None
            }
        }


NOMS_CLUSTERS = {
    0: "Trains locaux (courte distance)",
    1: "Trains grandes lignes",
    2: "Trains longue distance / internationaux",
    3: "Liaisons atypiques / outliers",
    4: "Trains a faible frequence",
}

TYPE_LIGNE_LABELS = {0: "Grande vitesse", 1: "Intercite", 2: "Regional"}
TYPE_SERVICE_LABELS = {0: "Jour", 1: "Nuit"}


class PredictResponse(BaseModel):
    duree_estimee_h: float = Field(..., description="Durée estimée du trajet en heures")
    duree_estimee_hhmm: str = Field(..., description="Durée estimée formatée (ex: 4h30)")
    substituable: bool = Field(..., description="True si la liaison peut remplacer un vol court-courrier")
    substituable_probabilite: float = Field(..., description="Probabilité de substituabilité (0.0 à 1.0)")
    cluster: int = Field(..., description="Identifiant du cluster K-Means")
    cluster_nom: str = Field(..., description="Nom de la famille de liaison")
    type_ligne_label: str
    type_service_label: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=PredictResponse, summary="Prédiction ML — durée, substituabilité, famille")
def predict(req: PredictRequest):
    """
    Effectue 3 prédictions sur une liaison ferroviaire :

    - **Régression** : durée estimée du trajet (RandomForest, R²=0.952)
    - **Classification** : cette liaison peut-elle remplacer un vol court-courrier ?
    - **Clustering** : famille de liaison (K-Means, 5 clusters)
    """
    m = get_models()

    # 1. Régression — prédire duree_h
    X_reg = pd.DataFrame([{
        "distance_km":       req.distance_km,
        "type_ligne_enc":    req.type_ligne,
        "type_service_enc":  req.type_service,
        "frequence_hebdo":   req.frequence_hebdo,
        "emissions_co2_gkm": req.emissions_co2_gkm,
    }])
    duree_pred = float(m["reg"].predict(X_reg)[0])
    heures = int(duree_pred)
    minutes = int((duree_pred - heures) * 60)

    # 2. Classification — substituable ?
    duree_clf = req.duree_h if req.duree_h is not None else duree_pred
    X_clf = pd.DataFrame([{
        "distance_km":       req.distance_km,
        "duree_h":           duree_clf,
        "type_ligne_enc":    req.type_ligne,
        "frequence_hebdo":   req.frequence_hebdo,
        "emissions_co2_gkm": req.emissions_co2_gkm,
    }])
    sub_pred = int(m["clf"].predict(X_clf)[0])
    sub_proba = float(m["clf"].predict_proba(X_clf)[0][1])

    # 3. Clustering — famille
    X_clu = pd.DataFrame([{
        "distance_km":       req.distance_km,
        "duree_h":           duree_clf,
        "frequence_hebdo":   req.frequence_hebdo,
        "emissions_co2_gkm": req.emissions_co2_gkm,
    }])
    X_scaled = m["scaler"].transform(X_clu)
    cluster = int(m["km"].predict(X_scaled)[0])

    return PredictResponse(
        duree_estimee_h=round(duree_pred, 2),
        duree_estimee_hhmm=f"{heures}h{minutes:02d}",
        substituable=bool(sub_pred == 1),
        substituable_probabilite=round(sub_proba, 3),
        cluster=cluster,
        cluster_nom=NOMS_CLUSTERS.get(cluster, f"Cluster {cluster}"),
        type_ligne_label=TYPE_LIGNE_LABELS.get(req.type_ligne, "Inconnu"),
        type_service_label=TYPE_SERVICE_LABELS.get(req.type_service, "Inconnu"),
    )


@router.get("/status", summary="Statut des modèles ML")
def predict_status():
    """Vérifie si les modèles ML sont chargés et disponibles."""
    available = all(
        os.path.exists(os.path.join(MODEL_DIR, f))
        for f in ["model_regression.pkl", "model_classification.pkl", "model_clustering.pkl"]
    )
    return {
        "modeles_disponibles": available,
        "model_dir": MODEL_DIR,
        "modeles": {
            "regression":     "RandomForest — R²=0.952 — cible: duree_h",
            "classification": "RandomForest — F1=1.0  — cible: substituable avion->train",
            "clustering":     "K-Means k=5  — silhouette=0.604 — familles de liaisons",
        }
    }
