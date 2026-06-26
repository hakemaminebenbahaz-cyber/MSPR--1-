"""
predict.py — ObRail Europe
Script de prediction autonome — utilise les modeles sauvegardes (.pkl)
sans avoir besoin de reentraine.

Usage :
  python predict.py
  python predict.py --distance 450 --duree 4.5 --frequence 5 --type_ligne 0 --co2 14

3 predictions :
  1. Duree estimee du trajet       (regression)
  2. Substituable avion->train ?   (classification)
  3. Famille de liaison            (clustering)
"""

import os
import sys
import argparse
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


# ── Chargement des modeles ────────────────────────────────────────────────────
def load_models():
    reg = joblib.load(f"{MODEL_DIR}/model_regression.pkl")
    clf = joblib.load(f"{MODEL_DIR}/model_classification.pkl")
    km, scaler = joblib.load(f"{MODEL_DIR}/model_clustering.pkl")
    return reg, clf, km, scaler


# ── Prediction ────────────────────────────────────────────────────────────────
def predict(distance_km, type_ligne_enc, type_service_enc,
            frequence_hebdo, emissions_co2_gkm, duree_h=None):

    reg, clf, km, scaler = load_models()

    print("\n" + "="*55)
    print("  Prediction ObRail Europe")
    print("="*55)
    print(f"  Distance        : {distance_km} km")
    print(f"  Type ligne      : {['Grande vitesse','Intercite','Regional'][type_ligne_enc]}")
    print(f"  Service         : {'Jour' if type_service_enc == 0 else 'Nuit'}")
    print(f"  Frequence       : {frequence_hebdo} fois/semaine")
    print(f"  Emissions CO2   : {emissions_co2_gkm} g/km")

    # ── 1. Regression : predire duree_h ──────────────────────────────────────
    X_reg = pd.DataFrame([{
        "distance_km":      distance_km,
        "type_ligne_enc":   type_ligne_enc,
        "type_service_enc": type_service_enc,
        "frequence_hebdo":  frequence_hebdo,
        "emissions_co2_gkm": emissions_co2_gkm,
    }])
    duree_pred = reg.predict(X_reg)[0]
    heures = int(duree_pred)
    minutes = int((duree_pred - heures) * 60)

    print(f"\n[REGRESSION] Duree estimee du trajet")
    print(f"  -> {duree_pred:.2f} h  ({heures}h{minutes:02d}min)")

    # ── 2. Classification : substituable avion->train ? ───────────────────────
    if duree_h is None:
        duree_h = duree_pred  # utilise la prediction si pas fournie

    X_clf = pd.DataFrame([{
        "distance_km":      distance_km,
        "duree_h":          duree_h,
        "type_ligne_enc":   type_ligne_enc,
        "frequence_hebdo":  frequence_hebdo,
        "emissions_co2_gkm": emissions_co2_gkm,
    }])
    sub_pred = clf.predict(X_clf)[0]
    sub_proba = clf.predict_proba(X_clf)[0][1] if hasattr(clf, 'predict_proba') else None

    print(f"\n[CLASSIFICATION] Substituable au vol court-courrier ?")
    if sub_pred == 1:
        print(f"  -> OUI — cette liaison peut remplacer un vol", end="")
    else:
        print(f"  -> NON — cette liaison ne remplace pas un vol", end="")
    if sub_proba is not None:
        print(f"  (probabilite : {sub_proba*100:.1f}%)")
    else:
        print()

    # ── 3. Clustering : famille de liaison ───────────────────────────────────
    X_clu = pd.DataFrame([{
        "distance_km":      distance_km,
        "duree_h":          duree_h,
        "frequence_hebdo":  frequence_hebdo,
        "emissions_co2_gkm": emissions_co2_gkm,
    }])
    X_scaled = scaler.transform(X_clu)
    cluster = km.predict(X_scaled)[0]

    noms_clusters = {
        0: "Trains locaux (courte distance)",
        1: "Trains grandes lignes",
        2: "Trains longue distance / internationaux",
        3: "Liaisons atypiques / outliers",
        4: "Trains a faible frequence",
    }
    nom = noms_clusters.get(cluster, f"Cluster {cluster}")

    print(f"\n[CLUSTERING] Famille de liaison identifiee")
    print(f"  -> Cluster {cluster} : {nom}")

    print("\n" + "="*55)
    return {
        "duree_estimee_h": round(float(duree_pred), 2),
        "substituable": bool(sub_pred == 1),
        "cluster": int(cluster),
        "cluster_nom": nom,
    }


# ── Exemples predefinies ──────────────────────────────────────────────────────
def run_examples():
    print("\n*** EXEMPLE 1 : Paris-Lyon (Grande vitesse, 450km) ***")
    predict(distance_km=450, type_ligne_enc=0, type_service_enc=0,
            frequence_hebdo=7, emissions_co2_gkm=14, duree_h=2.0)

    print("\n*** EXEMPLE 2 : Train regional court (50km) ***")
    predict(distance_km=50, type_ligne_enc=2, type_service_enc=0,
            frequence_hebdo=7, emissions_co2_gkm=32, duree_h=1.0)

    print("\n*** EXEMPLE 3 : Train de nuit Paris-Berlin (1000km) ***")
    predict(distance_km=1000, type_ligne_enc=1, type_service_enc=1,
            frequence_hebdo=3, emissions_co2_gkm=11, duree_h=13.0)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prediction ObRail Europe")
    parser.add_argument("--distance",    type=float, default=None)
    parser.add_argument("--duree",       type=float, default=None)
    parser.add_argument("--frequence",   type=float, default=None)
    parser.add_argument("--type_ligne",  type=int,   default=None,
                        help="0=Grande vitesse, 1=Intercite, 2=Regional")
    parser.add_argument("--type_service",type=int,   default=None,
                        help="0=Jour, 1=Nuit")
    parser.add_argument("--co2",         type=float, default=None)
    args = parser.parse_args()

    if args.distance is not None:
        # Mode ligne de commande
        predict(
            distance_km=args.distance,
            type_ligne_enc=args.type_ligne or 2,
            type_service_enc=args.type_service or 0,
            frequence_hebdo=args.frequence or 5,
            emissions_co2_gkm=args.co2 or 32,
            duree_h=args.duree,
        )
    else:
        # Mode demonstration avec 3 exemples
        run_examples()
