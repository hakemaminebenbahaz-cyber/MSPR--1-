"""
train.py — ObRail Europe
Entrainement de modeles pour trois taches :
  1. Regression     — Predire la duree du trajet (duree_h)
  2. Classification — Predire si une liaison peut remplacer un vol court-courrier
  3. Clustering     — Identifier les familles de liaisons (K-Means)

Workflow : chargement -> entrainement -> evaluation -> selection -> sauvegarde
"""

import os
import warnings
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             accuracy_score, f1_score, precision_score, recall_score,
                             silhouette_score)
from sklearn.model_selection import cross_val_score, GridSearchCV
from xgboost import XGBRegressor, XGBClassifier

warnings.filterwarnings("ignore")

RANDOM_STATE = 42
DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


# ── Chargement des données ────────────────────────────────────────────────────
def load_data():
    X_reg_tr = pd.read_csv(f"{DATA_DIR}/X_reg_train.csv")
    X_reg_te = pd.read_csv(f"{DATA_DIR}/X_reg_test.csv")
    y_reg_tr = pd.read_csv(f"{DATA_DIR}/y_reg_train.csv").squeeze()
    y_reg_te = pd.read_csv(f"{DATA_DIR}/y_reg_test.csv").squeeze()

    X_clf_tr = pd.read_csv(f"{DATA_DIR}/X_clf_train.csv")
    X_clf_te = pd.read_csv(f"{DATA_DIR}/X_clf_test.csv")
    y_clf_tr = pd.read_csv(f"{DATA_DIR}/y_clf_train.csv").squeeze()
    y_clf_te = pd.read_csv(f"{DATA_DIR}/y_clf_test.csv").squeeze()

    X_clu    = pd.read_csv(f"{DATA_DIR}/X_cluster.csv")

    print(f"Regression     — Train: {len(X_reg_tr):,}  Test: {len(X_reg_te):,}")
    print(f"Classification — Train: {len(X_clf_tr):,}  Test: {len(X_clf_te):,}")
    print(f"Clustering     — {len(X_clu):,} lignes")
    return (X_reg_tr, X_reg_te, y_reg_tr, y_reg_te,
            X_clf_tr, X_clf_te, y_clf_tr, y_clf_te, X_clu)


# ── 1. REGRESSION — Prédire duree_h ──────────────────────────────────────────
def train_regression(X_tr, X_te, y_tr, y_te):
    print("\n" + "="*55)
    print("  REGRESSION — Prediction duree_h")
    print("="*55)

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest":     RandomForestRegressor(n_estimators=50, random_state=RANDOM_STATE, n_jobs=1),
        "XGBoost":          XGBRegressor(n_estimators=50, random_state=RANDOM_STATE,
                                         eval_metric="rmse", verbosity=0),
        "MLP":              MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=200,
                                         random_state=RANDOM_STATE),
    }

    results = []
    trained = {}

    for name, model in models.items():
        print(f"\n  Entrainement {name}...")

        # Cross-validation 5 folds sur le train set
        cv_scores = cross_val_score(model, X_tr, y_tr, cv=3,
                                    scoring="neg_mean_absolute_error", n_jobs=1)
        cv_mae = -cv_scores.mean()

        # Entraînement final + évaluation sur le test set
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        mae  = mean_absolute_error(y_te, y_pred)
        rmse = np.sqrt(mean_squared_error(y_te, y_pred))
        r2   = r2_score(y_te, y_pred)

        print(f"    CV MAE={cv_mae:.3f}  |  Test MAE={mae:.3f}  RMSE={rmse:.3f}  R2={r2:.3f}")
        results.append({"Modele": name, "CV_MAE": round(cv_mae,3),
                         "MAE": round(mae,3), "RMSE": round(rmse,3), "R2": round(r2,3)})
        trained[name] = model

    df_results = pd.DataFrame(results).sort_values("R2", ascending=False)
    print("\n--- Tableau comparatif Regression ---")
    print(df_results.to_string(index=False))

    best_name = df_results.iloc[0]["Modele"]
    best_model = trained[best_name]
    print(f"\nMeilleur modele : {best_name}  (R2={df_results.iloc[0]['R2']})")

    # GridSearch sur le meilleur modèle
    best_model, best_name = optimize_regression(best_name, X_tr, y_tr, X_te, y_te)

    joblib.dump(best_model, f"{MODEL_DIR}/model_regression.pkl")
    print(f"Modele sauvegarde : ml/models/model_regression.pkl")

    df_results.to_csv(f"{DATA_DIR}/../reports/tableau_regression.csv", index=False)
    return df_results, best_model


def optimize_regression(best_name, X_tr, y_tr, X_te, y_te):
    print(f"\n  GridSearch sur {best_name}...")

    if best_name == "RandomForest":
        grid = GridSearchCV(
            RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1),
            param_grid={"n_estimators": [50, 100], "max_depth": [10, 20]},
            cv=3, scoring="neg_mean_absolute_error", n_jobs=1
        )
    elif best_name == "XGBoost":
        grid = GridSearchCV(
            XGBRegressor(random_state=RANDOM_STATE, verbosity=0, eval_metric="rmse"),
            param_grid={"n_estimators": [50, 100], "learning_rate": [0.05, 0.1],
                        "max_depth": [3, 6]},
            cv=3, scoring="neg_mean_absolute_error", n_jobs=1
        )
    else:
        print(f"  Pas de GridSearch pour {best_name}")
        if best_name == "LinearRegression":
            return LinearRegression().fit(X_tr, y_tr), best_name
        else:
            return MLPRegressor(hidden_layer_sizes=(64,32), max_iter=300,
                                random_state=RANDOM_STATE).fit(X_tr, y_tr), best_name

    grid.fit(X_tr, y_tr)
    print(f"  Meilleurs params : {grid.best_params_}")
    y_pred = grid.best_estimator_.predict(X_te)
    r2 = r2_score(y_te, y_pred)
    mae = mean_absolute_error(y_te, y_pred)
    print(f"  Apres GridSearch — MAE={mae:.3f}  R2={r2:.3f}")
    return grid.best_estimator_, best_name


# ── 2. CLASSIFICATION — Substituabilite avion->train ─────────────────────────
def train_classification(X_tr, X_te, y_tr, y_te):
    print("\n" + "="*55)
    print("  CLASSIFICATION — Liaison substituable avion->train ?")
    print("="*55)

    models = {
        "LogisticRegression": LogisticRegression(max_iter=500, random_state=RANDOM_STATE),
        "RandomForest":       RandomForestClassifier(n_estimators=50, random_state=RANDOM_STATE,
                                                     class_weight="balanced", n_jobs=1),
        "XGBoost":            XGBClassifier(n_estimators=50, random_state=RANDOM_STATE,
                                             eval_metric="logloss", verbosity=0,
                                             scale_pos_weight=(y_tr==0).sum()/(y_tr==1).sum()),
        "MLP":                MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300,
                                             random_state=RANDOM_STATE),
    }

    results = []
    trained = {}

    for name, model in models.items():
        print(f"\n  Entrainement {name}...")

        cv_scores = cross_val_score(model, X_tr, y_tr, cv=3,
                                    scoring="f1_weighted", n_jobs=1)
        cv_f1 = cv_scores.mean()

        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        acc  = accuracy_score(y_te, y_pred)
        f1   = f1_score(y_te, y_pred, average="weighted")
        prec = precision_score(y_te, y_pred, average="weighted", zero_division=0)
        rec  = recall_score(y_te, y_pred, average="weighted")

        print(f"    CV F1={cv_f1:.3f}  |  Test Acc={acc:.3f}  F1={f1:.3f}  Prec={prec:.3f}  Rec={rec:.3f}")
        results.append({"Modele": name, "CV_F1": round(cv_f1,3), "Accuracy": round(acc,3),
                         "F1": round(f1,3), "Precision": round(prec,3), "Recall": round(rec,3)})
        trained[name] = model

    df_results = pd.DataFrame(results).sort_values("F1", ascending=False)
    print("\n--- Tableau comparatif Classification ---")
    print(df_results.to_string(index=False))

    best_name = df_results.iloc[0]["Modele"]
    best_model = trained[best_name]
    print(f"\nMeilleur modele : {best_name}  (F1={df_results.iloc[0]['F1']})")

    joblib.dump(best_model, f"{MODEL_DIR}/model_classification.pkl")
    print(f"Modele sauvegarde : ml/models/model_classification.pkl")

    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "reports"), exist_ok=True)
    df_results.to_csv(f"{MODEL_DIR}/../reports/tableau_classification.csv", index=False)
    return df_results, best_model


# ── 3. CLUSTERING — Familles de liaisons (K-Means) ───────────────────────────
def train_clustering(X):
    print("\n" + "="*55)
    print("  CLUSTERING — Familles de liaisons ferroviaires")
    print("="*55)

    # Normalisation obligatoire pour K-Means
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Trouver le meilleur k avec le silhouette score (k entre 2 et 5)
    print("\n  Recherche du meilleur k...")
    scores = {}
    for k in range(2, 6):
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = km.fit_predict(X_scaled)
        sil = silhouette_score(X_scaled, labels, sample_size=5000, random_state=RANDOM_STATE)
        scores[k] = round(sil, 3)
        print(f"    k={k}  silhouette={sil:.3f}")

    best_k = max(scores, key=scores.get)
    print(f"\n  Meilleur k : {best_k}  (silhouette={scores[best_k]})")

    # Entraînement final
    best_km = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
    best_km.fit(X_scaled)
    labels = best_km.labels_

    # Description des clusters
    X_result = X.copy()
    X_result["cluster"] = labels
    print("\n  Description des clusters :")
    print(X_result.groupby("cluster")[["distance_km","duree_h","frequence_hebdo"]].mean().round(2))

    # Nommage des clusters selon distance moyenne
    cluster_means = X_result.groupby("cluster")["distance_km"].mean().sort_values()
    noms = {idx: nom for idx, (_, nom) in enumerate(zip(
        cluster_means.index,
        ["Trains locaux", "Trains grandes lignes", "Trains longue distance", "Trains nuit / internationaux"][:best_k]
    ))}
    # Associer le nom au bon cluster par distance
    nom_map = dict(zip(cluster_means.index, list(noms.values())))
    X_result["cluster_nom"] = X_result["cluster"].map(nom_map)
    print("\n  Repartition par cluster :")
    print(X_result["cluster_nom"].value_counts())

    # Sauvegarde
    joblib.dump((best_km, scaler), f"{MODEL_DIR}/model_clustering.pkl")
    X_result[["cluster","cluster_nom"]].to_csv(f"{MODEL_DIR}/../reports/tableau_clustering.csv", index=False)
    print(f"\n  Modele sauvegarde : ml/models/model_clustering.pkl")

    return best_km, scaler, best_k


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Entrainement des modeles — ObRail Europe")
    print("=" * 55)

    (X_reg_tr, X_reg_te, y_reg_tr, y_reg_te,
     X_clf_tr, X_clf_te, y_clf_tr, y_clf_te, X_clu) = load_data()

    df_reg, model_reg = train_regression(X_reg_tr, X_reg_te, y_reg_tr, y_reg_te)
    df_clf, model_clf = train_classification(X_clf_tr, X_clf_te, y_clf_tr, y_clf_te)
    km, scaler, best_k = train_clustering(X_clu)

    print("\n" + "="*55)
    print("  RESUME FINAL")
    print("="*55)
    print("\nRegression (duree_h) :")
    print(df_reg.to_string(index=False))
    print("\nClassification (substituabilite avion->train) :")
    print(df_clf.to_string(index=False))
    print(f"\nClustering : {best_k} familles de liaisons identifiees")
    print("\n[OK] Etape 3 terminee - modeles dans ml/models/")
