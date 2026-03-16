# ObRail Europe — Observatoire Ferroviaire Européen

Projet MSPR — EPSI Bloc E6.1 RNCP36581
Étudiant : Hakem | Mars 2026

---

## Présentation

Pipeline complet de données ferroviaires européennes :
**Sources GTFS open data → ETL Python → PostgreSQL Azure → API FastAPI → Dashboard React**

- ~2 900 dessertes, 55 opérateurs, 6 190 gares (FR, BE, DE, AT + trains de nuit internationaux)
- Sources : SNCF TER, SNCF Intercités, Deutsche Bahn, SNCB, ÖBB, Open Night Train Database

---

## Prérequis

- Python 3.12+
- Node.js 20+
- PostgreSQL (ou Azure Database for PostgreSQL)
- Un fichier `.env` à la racine (voir `.env.example`)

---

## Installation

```bash
git clone https://github.com/hakemaminebenbahaz-cyber/MSPR--1-
cd "MSPR -1-"
```

### 1. Variables d'environnement

```bash
cp .env.example .env
# Renseigner DATABASE_URL dans .env
```

### 2. Créer le schéma de la base de données

```bash
psql $DATABASE_URL -f database/schema.sql
```

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

---

## Lancer le pipeline ETL

Le pipeline complet : téléchargement GTFS → transformation → insertion en base.

```bash
python etl/orchestre.py
```

Pour relancer uniquement la transformation + le chargement (sans re-télécharger) :

```bash
python etl/orchestre.py --skip-extract
```

### Étapes du pipeline

| Étape | Script | Description |
|-------|--------|-------------|
| Extract | `etl/extract/extract_gtfs.py` | Télécharge les archives GTFS (SNCF, DB, SNCB, ÖBB) |
| Extract | `etl/extract/extract_opendata.py` | Télécharge l'Open Night Train Database |
| Transform | `etl/transform/transform_gtfs.py` | Nettoie et fusionne → operateurs.csv, gares.csv, dessertes.csv |
| Transform | `etl/transform/transform_night_trains.py` | Transforme les trains de nuit |
| Load | `etl/load/load_to_postgresql.py` | Insère les CSV dans PostgreSQL |

---

## Lancer l'API

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Documentation Swagger disponible sur : `http://localhost:8000/docs`

Authentification : header `X-API-Key: obrail-api-key-2026`

---

## Lancer le Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Dashboard disponible sur : `http://localhost:5173`

---

## Lancer avec Docker

```bash
cp .env.example .env
# Renseigner DATABASE_URL dans .env

docker-compose up --build
```

- API : `http://localhost:8000`
- Dashboard : `http://localhost:5173`

---

## Structure du projet

```
MSPR -1-/
├── etl/
│   ├── extract/          # Téléchargement des sources GTFS et open data
│   ├── transform/        # Nettoyage et fusion des données
│   ├── load/             # Insertion en base PostgreSQL
│   └── orchestre.py      # Point d'entrée du pipeline ETL
├── api/
│   ├── routers/          # Endpoints FastAPI
│   ├── models/           # Modèles SQLAlchemy
│   ├── schemas/          # Schémas Pydantic
│   └── main.py           # Point d'entrée de l'API
├── dashboard/
│   └── src/
│       └── pages/        # VueGlobale, Recherche, DonneesBrutes
├── database/
│   └── schema.sql        # Schéma PostgreSQL (CREATE TABLE)
├── docs/
│   ├── documentation_technique.pdf
│   └── ObRail_API_Postman.json
├── docker-compose.yml
├── run_etl.sh            # Script ETL pour Azure Batch
└── .env.example
```

---

## Tests API

La collection Postman est disponible dans `docs/ObRail_API_Postman.json`.

Principaux endpoints :

| Endpoint | Description |
|----------|-------------|
| `GET /health` | État de l'API |
| `GET /api/v1/operateurs/` | Liste des opérateurs |
| `GET /api/v1/gares/` | Liste des gares |
| `GET /api/v1/dessertes/` | Liste des dessertes (filtres disponibles) |
| `GET /api/v1/comparisons/stats-globales` | Statistiques globales |
| `GET /api/v1/comparisons/qualite-donnees` | Taux de complétude par table |
