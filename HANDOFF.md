# HANDOFF — MSPR ObRail Europe
## Résumé complet de tout ce qui a été fait
**Auteur : BENBAHAZ Hakem Amine**
**Date : Juin 2026**

---

## C'est quoi le projet

**ObRail Europe** = observatoire ferroviaire européen fictif (projet EPSI, Bloc E6.1 RNCP36581).

**Objectif** : construire un pipeline complet de données ferroviaires européennes (SNCF + DB Germany) :
- ETL (Extract / Transform / Load) → base PostgreSQL Azure
- API REST FastAPI pour consulter les données
- Module ML avec 3 modèles prédictifs (IA)
- Dashboard React pour visualiser

**Répartition du travail :**
- **Hakem** → ETL + API FastAPI + Module ML + Tests
- **Ami** → Infrastructure Azure (ADF, PostgreSQL Azure, DATABASE_URL)

---

## Repo GitHub

```
https://github.com/hakemaminebenbahaz-cyber/MSPR--1-
```

**Branches** : tout est sur `main`

---

## Structure du projet

```
MSPR--1-/
├── api/                        ← API FastAPI (Python)
│   ├── main.py                 ← point d'entrée, tous les routers
│   ├── routers/
│   │   ├── gares.py
│   │   ├── dessertes.py
│   │   ├── operateurs.py
│   │   ├── comparisons.py
│   │   └── predict.py          ← endpoint ML /api/v1/predict
│   ├── models/                 ← modèles SQLAlchemy
│   ├── schemas/                ← schémas Pydantic
│   └── core/                   ← config, database, dependencies, security
├── ml/                         ← Module IA (MSPR E6.2+E6.4)
│   ├── scripts/
│   │   ├── prepare_data.py     ← nettoyage + feature engineering
│   │   ├── train.py            ← entraînement 3 modèles
│   │   └── predict.py          ← prédictions standalone
│   ├── tests/
│   │   └── test_model.py       ← 20 tests pytest
│   ├── reports/
│   │   ├── tableau_regression.csv
│   │   ├── tableau_classification.csv
│   │   ├── tableau_clustering.csv
│   │   └── benchmark_cloud_ia.md
│   ├── data/                   ← CSV générés (ignorés par git)
│   ├── models/                 ← .pkl générés (ignorés par git)
│   └── requirements_ml.txt
├── etl/                        ← scripts ETL
├── dashboard/                  ← React + TypeScript + Vite
├── data/
│   └── transformed/
│       └── dessertes.csv       ← 122 801 lignes (source des modèles ML)
├── rapport_ml.md               ← rapport technique ML complet
├── rapport_ml.pdf              ← version PDF
└── requirements.txt
```

---

## Partie 1 — API FastAPI

### Comment lancer

```bash
cd api
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

**Documentation Swagger** : http://localhost:8000/docs

### Authentification

Tous les endpoints `/api/v1/*` nécessitent un header :
```
X-API-Key: <valeur dans le .env>
```

### Endpoints disponibles

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/gares` | Liste des gares (filtre par nom, pays) |
| GET | `/api/v1/dessertes` | Liaisons ferroviaires (filtre départ/arrivée/type) |
| GET | `/api/v1/operateurs` | Opérateurs ferroviaires |
| GET | `/api/v1/comparisons` | Analyses comparatives |
| POST | `/api/v1/predict` | **Prédictions ML** (voir ci-dessous) |
| GET | `/api/v1/predict/status` | Statut des modèles ML |
| GET | `/health` | Santé de l'API |

### Variables d'environnement (.env)

```
DATABASE_URL=postgresql://user:password@host/dbname   ← fourni par l'ami (Azure)
SECRET_KEY=...
API_KEY=...
```

---

## Partie 2 — Module ML (MSPR E6.2+E6.4)

### Installation

```bash
pip install -r ml/requirements_ml.txt
```

### Pipeline complet (dans l'ordre)

```bash
# 1. Préparer les données
python -u ml/scripts/prepare_data.py

# 2. Entraîner les 3 modèles
python -u ml/scripts/train.py

# 3. Tester les prédictions
python -u ml/scripts/predict.py

# 4. Lancer les tests
pytest ml/tests/test_model.py -v
```

> Les fichiers `.pkl` (modèles) et `.csv` (données) ne sont pas sur GitHub (trop lourds).
> Il faut les régénérer en local avec les 2 premières commandes.

### Les 3 modèles

#### Modèle 1 — Régression (prédire la durée du trajet)

- **Cible** : `duree_h` (durée en heures)
- **Features** : distance_km, type_ligne_enc, type_service_enc, frequence_hebdo, emissions_co2_gkm
- **Meilleur modèle** : RandomForest — **R²=0.952**, MAE=6 min
- **Fichier** : `ml/models/model_regression.pkl`

| Modèle | R² | MAE |
|--------|----|-----|
| RandomForest | **0.952** | 6 min |
| XGBoost | 0.913 | 10 min |
| MLP | 0.861 | 12 min |
| LinearRegression | 0.141 | 35 min |

#### Modèle 2 — Classification (substituabilité avion→train)

- **Cible** : `substituable` (0 ou 1)
- **Règle** : `distance >= 150km AND duree < 8h AND frequence >= 2/sem` → 7.3% positifs
- **Meilleur modèle** : RandomForest — **F1=1.0** ⚠️
- **Limitation** : F1=1.0 car la cible est construite à partir des mêmes features (data leakage — documenté)
- **Fichier** : `ml/models/model_classification.pkl`

#### Modèle 3 — Clustering K-Means (familles de liaisons)

- **Non supervisé** — découvre les groupes automatiquement
- **k=5** choisi par silhouette score (0.604)
- **5 familles** : trains locaux, grandes lignes, longue distance, faible fréquence, outliers
- **Fichier** : `ml/models/model_clustering.pkl` (tuple KMeans + StandardScaler)

### Endpoint /predict — exemple complet

**Requête :**
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "X-API-Key: <clé>" \
  -H "Content-Type: application/json" \
  -d '{
    "distance_km": 450,
    "type_ligne": 0,
    "type_service": 0,
    "frequence_hebdo": 7,
    "emissions_co2_gkm": 14
  }'
```

**Réponse :**
```json
{
  "duree_estimee_h": 4.92,
  "duree_estimee_hhmm": "4h55",
  "substituable": true,
  "substituable_probabilite": 0.98,
  "cluster": 2,
  "cluster_nom": "Trains longue distance / internationaux",
  "type_ligne_label": "Grande vitesse",
  "type_service_label": "Jour"
}
```

**Encodage type_ligne :** `0=Grande vitesse`, `1=Intercité`, `2=Régional`
**Encodage type_service :** `0=Jour`, `1=Nuit`

### Tests — 20/20

```
pytest ml/tests/test_model.py -v
→ 20 passed in 5.06s
```

| Classe | Nb tests | Ce que ça vérifie |
|--------|----------|-------------------|
| TestChargementModeles | 4 | Fichiers .pkl accessibles |
| TestRegression | 6 | Cohérence métier (TGV > régional, distance → durée) |
| TestClassification | 5 | Paris-Lyon substituable, 30km non substituable |
| TestClustering | 5 | Cluster valide (0-4), reproductibilité |

---

## Partie 3 — Ce qui reste à faire

| Tâche | Responsable | Statut |
|-------|-------------|--------|
| Rapport technique ML | Hakem | ✅ `rapport_ml.pdf` |
| Slides soutenance | Hakem | ❌ À faire (Canva/PPT) |
| Infrastructure Azure ML (optionnel) | Ami | ❌ |

---

## Résultats clés à retenir pour la soutenance

| Modèle | Métrique | Résultat |
|--------|---------|---------|
| Régression RandomForest | R² | **0.952** (95% variance expliquée) |
| Régression RandomForest | MAE | **6 minutes** d'erreur moyenne |
| Classification RandomForest | F1 | **1.0** (limitation data leakage documentée) |
| Clustering K-Means k=5 | Silhouette | **0.604** (clusters bien séparés) |
| Tests pytest | Résultat | **20/20 passés** |
| Dataset | Volume | **122 801 liaisons** ferroviaires |

---

## Fichiers importants sur GitHub

| Fichier | Description |
|---------|-------------|
| `rapport_ml.pdf` | Rapport technique complet (à rendre au jury) |
| `ml/README.md` | Documentation du module ML |
| `ml/reports/benchmark_cloud_ia.md` | Comparatif Azure ML / AWS / Google / HuggingFace |
| `ml/reports/tableau_regression.csv` | Résultats comparatifs régression |
| `ml/reports/tableau_classification.csv` | Résultats comparatifs classification |
| `ml/scripts/prepare_data.py` | ETL + feature engineering |
| `ml/scripts/train.py` | Entraînement des 3 modèles |
| `ml/scripts/predict.py` | Prédictions standalone |
| `ml/tests/test_model.py` | 20 tests pytest |
| `api/routers/predict.py` | Endpoint REST /api/v1/predict |

---

*Document de passation — ObRail Europe — MSPR EPSI — Juin 2026*
