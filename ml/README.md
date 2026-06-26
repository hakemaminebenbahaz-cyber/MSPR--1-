# Module ML — ObRail Europe
**MSPR E6.2 + E6.4 — Développement d'un modèle prédictif IA**
**Auteur : Hakem**

---

## Contexte

ObRail Europe est un observatoire ferroviaire européen (projet EPSI, Bloc E6.1 RNCP36581).
Ce module ML analyse les données ferroviaires pour produire 3 modèles prédictifs couvrant les 3 familles exigées par la grille d'évaluation :

| Famille | Tâche | Cible |
|---------|-------|-------|
| Régression supervisée | Prédire la durée d'un trajet | `duree_h` |
| Classification supervisée | Une liaison peut-elle remplacer un vol court-courrier ? | `substituable` (0/1) |
| Clustering non supervisé | Identifier les familles de liaisons ferroviaires | K-Means, k=5 |

---

## Source des données

- Fichier : `data/transformed/dessertes.csv`
- Lignes : 122 801 liaisons ferroviaires européennes
- Format : CSV avec colonnes `distance_km`, `duree_h`, `type_ligne`, `type_service`, `frequence_hebdo`, `emissions_co2_gkm`, `traction`

---

## Pipeline complet

```
prepare_data.py  →  train.py  →  predict.py
                                     ↓
                              api/routers/predict.py  (TODO)
```

---

## Étapes réalisées

### Étape 1 — Préparation des données (`prepare_data.py`)

**Ce que fait le script :**
- Charge `dessertes.csv` (122 801 lignes)
- Nettoie : convertit les colonnes numériques, remplace les 59 valeurs manquantes de `frequence_hebdo` par la médiane
- Encode : `type_ligne` → 0/1/2, `type_service` → 0/1 (Jour/Nuit)
- **Supprime `traction`** : 99.7% électrique → aucune variance utile
- Crée la cible `substituable` (règle métier — voir ci-dessous)
- Sauvegarde les CSV dans `ml/data/`

**Règle substituabilité (cible classification) :**
```python
substituable = (distance_km >= 150) AND (duree_h < 8) AND (frequence_hebdo >= 2)
```
→ 8 970 / 122 801 liaisons substituables **(7.3%)**

> Note : seuil abaissé à 150km car le dataset est majoritairement des trains régionaux courts (médiane 42km). Les 300km+ sont rares.

**Features retenues :**

| Variable | Type | Utilisée pour |
|----------|------|--------------|
| `distance_km` | Numérique | Régression + Classification + Clustering |
| `duree_h` | Numérique | **Cible régression** / feature classification + clustering |
| `frequence_hebdo` | Numérique | Régression + Classification + Clustering |
| `emissions_co2_gkm` | Numérique | Régression + Classification + Clustering |
| `type_ligne_enc` | Catégoriel encodé (0/1/2) | Régression + Classification |
| `type_service_enc` | Catégoriel encodé (0/1) | Régression |
| `substituable` | Binaire créé | **Cible classification** |

---

### Étape 2 — Entraînement (`train.py`)

**Paramètres globaux :** `n_jobs=1` (fix Windows), `n_estimators=50`, `cv=3`

#### Régression — prédire `duree_h`

| Modèle | CV MAE | MAE test | RMSE | R² |
|--------|--------|----------|------|----|
| **RandomForest** | 0.101 | **0.097** | 0.212 | **0.952** |
| XGBoost | 0.167 | 0.167 | 0.285 | 0.913 |
| MLP | 0.215 | 0.201 | 0.360 | 0.861 |
| LinearRegression | 0.584 | 0.586 | 0.894 | 0.141 |

**Meilleur modèle : RandomForest** (R²=0.952, ~6 min d'erreur moyenne)
GridSearch confirmé : `max_depth=20`, `n_estimators=100`

LinearRegression à 0.14 montre que la relation est non-linéaire → bon argument pour la soutenance.

#### Classification — prédire `substituable`

| Modèle | CV F1 | Accuracy | F1 | Précision | Rappel |
|--------|-------|----------|----|-----------|--------|
| **RandomForest** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| XGBoost | 0.998 | 0.998 | 0.998 | 0.998 | 0.998 |
| MLP | 0.997 | 0.998 | 0.998 | 0.998 | 0.998 |
| LogisticRegression | 0.976 | 0.979 | 0.978 | 0.979 | 0.979 |

> ⚠️ **Limitation connue** : F1=1.0 est un signal d'alarme. La cible `substituable` a été construite à partir des mêmes features que l'entraînement → le modèle apprend trivialement la règle (data leakage). À mentionner dans le rapport et la soutenance comme limitation méthodologique.

#### Clustering — K-Means

Sélection automatique du meilleur k par silhouette score :

| k | Silhouette |
|---|-----------|
| 2 | 0.515 |
| 3 | 0.515 |
| 4 | 0.573 |
| **5** | **0.604** |

**5 clusters identifiés :**

| Cluster | Distance moy. | Durée moy. | Fréquence | Nb liaisons |
|---------|--------------|-----------|-----------|-------------|
| Trains locaux | 66 km | 1h07 | 6.1/sem | 66 225 |
| Trains longue distance | 44 km | 0h52 | 6.9/sem | 40 011 |
| Trains grandes lignes | 414 km | 4h16 | 6.2/sem | 11 578 |
| Trains nuit/internationaux | 17 720 km | 5h24 | 4.3/sem | 4 944 |

> Le cluster "17 720km" = **anomalies détectées automatiquement** (distances impossibles pour des trains européens). Bon point à présenter au jury : le clustering a trouvé des outliers dans les données.

---

### Étape 3 — Prédiction autonome (`predict.py`)

Script standalone qui charge les `.pkl` sans réentraîner.

**Usage basique (3 exemples automatiques) :**
```bash
python ml/scripts/predict.py
```

**Usage ligne de commande :**
```bash
python ml/scripts/predict.py --distance 450 --type_ligne 0 --frequence 7 --co2 14
```

Arguments :
- `--distance` : distance en km
- `--duree` : durée réelle en h (optionnel, sinon utilise la prédiction)
- `--frequence` : passages/semaine
- `--type_ligne` : 0=Grande vitesse, 1=Intercité, 2=Régional
- `--type_service` : 0=Jour, 1=Nuit
- `--co2` : émissions CO2 en g/km

Retourne les 3 prédictions : durée estimée, substituable oui/non, cluster.

---

## Installation

```bash
# Installer les dépendances
pip install -r ml/requirements_ml.txt

# 1. Préparer les données (génère les CSV dans ml/data/)
python -u ml/scripts/prepare_data.py

# 2. Entraîner les modèles (génère les .pkl dans ml/models/)
python -u ml/scripts/train.py

# 3. Tester les prédictions
python -u ml/scripts/predict.py
```

> Les fichiers `.pkl` (modèles) et `.csv` (données) sont exclus du repo GitHub (`.gitignore`).
> Il faut les régénérer en local.

---

## Ce qui reste à faire

- [ ] **Étape 5** — Endpoint `/predict` dans `api/routers/predict.py` (FastAPI)
- [ ] **Étape 6** — Tests pytest dans `ml/tests/test_model.py`
- [ ] **Étape 7** — Benchmark cloud IA (Azure ML vs AWS SageMaker vs Google AutoML)
- [ ] **Étape 8** — Rapport technique complet
- [ ] **Étape 9** — Soutenance Canva

---

## Structure des fichiers

```
ml/
├── scripts/
│   ├── prepare_data.py    ← ETL + feature engineering
│   ├── train.py           ← entraînement des 3 modèles
│   └── predict.py         ← prédictions autonomes
├── data/                  ← CSV générés (ignorés par git)
│   ├── X_reg_train.csv
│   ├── X_clf_train.csv
│   ├── X_cluster.csv
│   └── tableau_variables.csv
├── models/                ← .pkl générés (ignorés par git)
│   ├── model_regression.pkl
│   ├── model_classification.pkl
│   └── model_clustering.pkl
├── reports/               ← tableaux comparatifs (sur git)
│   ├── tableau_regression.csv
│   ├── tableau_classification.csv
│   └── tableau_clustering.csv
├── requirements_ml.txt
└── README.md
```
