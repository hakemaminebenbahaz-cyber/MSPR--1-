# Documentation Technique — ObRail Europe

**Projet MSPR — EPSI Bloc E6.1 RNCP36581**
**Étudiant : Hakem**
**Date : Mars 2026**

---

## 1. Présentation du projet

ObRail Europe est un projet de fin d'études réalisé dans le cadre du bloc E6.1 à l'EPSI. Le client fictif est un observatoire ferroviaire européen qui souhaite centraliser les données de dessertes ferroviaires de plusieurs pays européens, les rendre accessibles via une API, et les visualiser dans un dashboard.

L'objectif concret : construire un pipeline complet allant de la collecte de données brutes (fichiers GTFS publics) jusqu'à une interface web, en passant par une base de données PostgreSQL hébergée sur Azure.

Le projet est réparti entre deux étudiants :
- **Hakem** : scripts ETL (Extract/Transform/Load), API FastAPI, Dashboard React
- **Ami** : infrastructure Azure (ADF, Azure Batch, PostgreSQL Azure, réseau)

---

## 2. Architecture globale

```
Sources publiques (GTFS / CSV)
         │
         ▼
  ┌──────────────┐
  │  ETL Python  │  extract → transform → load
  └──────┬───────┘
         │  orchestré par Azure Data Factory (quotidien)
         ▼
  ┌──────────────────────┐
  │  PostgreSQL (Azure)  │  3 tables : operateurs, gares, dessertes
  └──────────┬───────────┘
             │
             ▼
  ┌────────────────┐
  │  API FastAPI   │  port 8000, Azure Web App
  └──────┬─────────┘
         │
         ▼
  ┌─────────────────────┐
  │  Dashboard React    │  Azure Web App
  └─────────────────────┘
```

Les scripts ETL tournent dans un pool Azure Batch (Ubuntu 22.04, nœuds `Standard_D2s_v3`). À chaque déclenchement, ADF lance un script `run_etl.sh` qui fait d'abord un `git pull` pour récupérer les dernières modifications, puis exécute le pipeline.

---

## 3. Sources de données

J'ai choisi des sources GTFS open data officielles pour chaque pays, complétées par une base CSV pour les trains de nuit :

| Source | Opérateur | Pays | Dessertes |
|--------|-----------|------|-----------|
| SNCF TER | SNCF | FR | ~896 |
| SNCF Intercités | SNCF VOYAGEURS | FR | ~47 |
| DB Germany | Deutsche Bahn | DE | ~89 |
| SNCB | SNCB | BE | ~1047 |
| ÖBB | OBB | AT | ~413 |
| Open Night Train DB | Back-on-Track | Multi | ~408 |

**Total : ~2900 dessertes, ~55 opérateurs, ~6190 gares**

Le format GTFS (General Transit Feed Specification) est un standard utilisé par la quasi-totalité des opérateurs ferroviaires européens. Chaque archive zip contient plusieurs fichiers texte : `agency.txt`, `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`, etc.

Les émissions CO2 (g/km) sont tirées du rapport EEA 2023 et varient selon le mix électrique national :
- France : 14 g/km
- Belgique : 18 g/km
- Allemagne : 32 g/km
- Autriche : 12 g/km

---

## 4. Pipeline ETL

### 4.1 Extract

L'extraction télécharge automatiquement les archives GTFS depuis les URLs officielles et les décompresse dans `data/raw/<source>/`. Pour l'Open Night Train Database, c'est un fichier CSV directement parsé.

### 4.2 Transform

C'est la partie la plus complexe du projet. Le script principal est `etl/transform/transform_gtfs.py` et il produit trois fichiers CSV dans `data/transformed/`.

**Étape 1 — Opérateurs**

On lit le fichier `agency.txt` de chaque source. Certains `agency_id` sont des UUIDs complexes (ex: `FR:Authority::REGION_ARA:...`) qu'on simplifie. On filtre aussi les faux opérateurs comme `OCEdefault` qui n'est pas un vrai opérateur mais une valeur par défaut de la SNCF. En cas de `agency_id` non trouvé lors du matching, on utilise un `operateur_defaut` défini par source.

**Étape 2 — Gares**

Le problème principal ici était le géocodage. Au départ j'utilisais le `pays_code` de la source GTFS pour affecter le pays d'une gare, mais ça donnait des résultats absurdes (Bruges classée en France parce que le fichier venait de SNCF TER). J'ai donc utilisé la bibliothèque `reverse_geocoder` qui fait un géocodage inverse par coordonnées GPS, basé sur les vraies frontières géographiques. Ça règle le problème proprement.

Pour la déduplication, on garde les `StopArea` (location_type=1) quand c'est disponible, sinon tous les arrêts. La clé de déduplication est `(nom, pays_code)` pour garder par exemple "Bruges-FR" et "Bruges-BE" séparément si elles existent vraiment dans deux pays différents.

**Étape 3 — Dessertes**

C'est le coeur du transform. Pour chaque source on :
1. Filtre uniquement les routes ferroviaires (route_type 2, 100-107)
2. Identifie le premier et dernier arrêt de chaque trip via `stop_times.txt`
3. Déduplique par `(route_id, direction_id)` en gardant le trip le plus long
4. Calcule la distance avec la formule haversine entre les coordonnées GPS des gares
5. Calcule la fréquence hebdomadaire depuis `calendar.txt` ou `calendar_dates.txt`
6. Détermine le type de service (Jour/Nuit) selon l'heure de départ

Un problème notable sur les fréquences : certains `service_id` dans `trips.txt` étaient stockés sans zéros de tête (`1`), alors que dans `calendar.txt` ils avaient des zéros (`000001`). La jointure donnait zéro résultat. J'ai ajouté une fonction `_norm_sid()` qui normalise les deux côtés en retirant les zéros de tête via `int(s)`.

**Calcul de la fréquence hebdomadaire :**
- Si `calendar.txt` contient des jours non nuls → on somme les colonnes lundi-dimanche
- Sinon on tombe sur `calendar_dates.txt` → on compte les dates actives sur la période totale, divisé par le nombre de semaines

**Typage automatique des lignes :**

```python
def _type_ligne(nom):
    if "tgv" in nom or "ice" in nom:       return "Grande vitesse"
    if "intercit" in nom or "ic " in nom:  return "Intercité"
    if "nuit" in nom or "nightjet" in nom: return "Train de nuit interne"
    return "Train régional"
```

### 4.3 Load

Le script de chargement lit les trois CSV et les insère dans PostgreSQL via SQLAlchemy. L'ordre d'insertion est important pour respecter les clés étrangères : opérateurs en premier, puis gares, puis dessertes. On résout les FK en faisant correspondre les noms d'opérateurs/gares avec les IDs insérés.

---

## 5. Base de données

La base PostgreSQL est hébergée sur Azure Database for PostgreSQL (Flexible Server). Elle contient trois tables.

### Schéma

**Table `operateurs`**
| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL PK | Identifiant auto |
| nom | VARCHAR(100) | Nom de l'opérateur |
| pays_code | CHAR(2) | Code pays ISO (FR, DE, BE, AT) |

**Table `gares`**
| Colonne | Type | Description |
|---------|------|-------------|
| id | SERIAL PK | Identifiant auto |
| nom | VARCHAR(150) | Nom de la gare |
| pays_code | CHAR(2) | Code pays ISO |
| latitude | NUMERIC(9,6) | Coordonnée GPS |
| longitude | NUMERIC(9,6) | Coordonnée GPS |

**Table `dessertes`**
| Colonne | Type | Description |
|---------|------|-------------|
| id | VARCHAR(20) PK | Ex: `FR_ROUTE01_0` |
| operateur_id | INT FK | Référence operateurs.id |
| nom_ligne | VARCHAR(200) | Nom de la ligne |
| type_ligne | VARCHAR(50) | Grande vitesse / Intercité / Train régional / Train de nuit interne |
| type_service | VARCHAR(10) | Jour ou Nuit |
| gare_depart_id | INT FK | Référence gares.id |
| gare_arrivee_id | INT FK | Référence gares.id |
| heure_depart | TIME | Heure de départ normalisée |
| heure_arrivee | TIME | Heure d'arrivée normalisée |
| distance_km | INT | Calculé par haversine |
| duree_h | NUMERIC(5,2) | Durée en heures |
| emissions_co2_gkm | NUMERIC(6,2) | En g/km (source EEA 2023) |
| frequence_hebdo | INT | Nombre de jours par semaine |
| traction | VARCHAR(20) | électrique / diesel |
| source_donnee | VARCHAR(100) | Ex: `GTFS sncf_ter` |

---

## 6. API REST

### Stack

- Python 3.12, FastAPI, SQLAlchemy ORM, psycopg2-binary, Pydantic v2
- Déployée sur Azure Web App, port 8000
- Documentation auto disponible sur `/docs` (Swagger UI)

### Authentification

Tous les endpoints sous `/api/v1/` nécessitent un header `X-API-Key`. La clé est vérifiée par un middleware HTTP avant chaque requête.

```
X-API-Key: <votre_clé>
```

### Endpoints

**GET /health** — Vérification que l'API tourne

```json
{"status": "healthy", "service": "ObRail API"}
```

---

**GET /api/v1/operateurs/**
Paramètre optionnel : `pays_code` (ex: `FR`)

```bash
curl -H "X-API-Key: xxx" "https://.../api/v1/operateurs/?pays_code=FR"
```

```json
[
  {"id": 1, "nom": "SNCF", "pays_code": "FR"},
  {"id": 2, "nom": "SNCF VOYAGEURS", "pays_code": "FR"}
]
```

---

**GET /api/v1/gares/**
Paramètres : `nom` (partiel), `pays_code`

```bash
curl -H "X-API-Key: xxx" "https://.../api/v1/gares/?nom=Paris&pays_code=FR"
```

---

**GET /api/v1/dessertes/**
Paramètres disponibles :

| Paramètre | Type | Description |
|-----------|------|-------------|
| depart | string | Nom partiel de la gare de départ |
| arrivee | string | Nom partiel de la gare d'arrivée |
| type_service | string | `Jour` ou `Nuit` |
| type_ligne | string | `Grande vitesse`, `Intercité`, etc. |
| operateur | string | Nom partiel de l'opérateur |
| pays_code | string | Pays de la gare de départ |
| skip | int | Pagination (défaut 0) |
| limit | int | Résultats max (défaut 100, max 500) |

```bash
curl -H "X-API-Key: xxx" \
  "https://.../api/v1/dessertes/?depart=Paris&arrivee=Bruxelles&type_service=Jour"
```

```json
[
  {
    "id": "FR_ROUTE42_0",
    "nom_ligne": "Paris Nord - Bruxelles Midi",
    "type_ligne": "Intercité",
    "type_service": "Jour",
    "gare_depart": {"id": 120, "nom": "Paris Nord", "pays_code": "FR"},
    "gare_arrivee": {"id": 87, "nom": "Bruxelles Midi", "pays_code": "BE"},
    "heure_depart": "07:13:00",
    "heure_arrivee": "09:22:00",
    "distance_km": 312,
    "duree_h": 2.15,
    "emissions_co2_gkm": 14.0,
    "frequence_hebdo": 7,
    "operateur": {"id": 1, "nom": "SNCF", "pays_code": "FR"}
  }
]
```

---

**GET /api/v1/dessertes/{id}** — Détail d'une desserte par ID

```bash
curl -H "X-API-Key: xxx" "https://.../api/v1/dessertes/FR_ROUTE42_0"
```

---

**GET /api/v1/comparisons/stats-globales** — Totaux généraux

```json
{
  "total_dessertes": 2900,
  "total_gares": 6190,
  "total_operateurs": 55
}
```

**GET /api/v1/comparisons/jour-vs-nuit** — Stats CO2 et durée par type de service

**GET /api/v1/comparisons/par-pays** — Nombre de dessertes par pays

**GET /api/v1/comparisons/par-operateur** — Classement des opérateurs par volume de dessertes

---

### Tests API (Postman)

Les tests ont été réalisés avec Postman. La collection complète est disponible dans `docs/ObRail_API_Postman.json`.

| # | Requête | Résultat attendu | Statut |
|---|---------|-----------------|--------|
| 1 | `GET /health` | `{"status": "ok", "database": "connected"}` | ✅ 200 |
| 2 | `GET /api/v1/gares?limit=10` | Liste de 10 gares avec nom, pays, coordonnées | ✅ 200 |
| 3 | `GET /api/v1/gares?pays_code=FR` | Gares françaises uniquement | ✅ 200 |
| 4 | `GET /api/v1/gares/99999` | Gare inexistante → erreur | ✅ 404 |
| 5 | `GET /api/v1/operateurs?pays_code=FR` | SNCF, SNCF VOYAGEURS | ✅ 200 |
| 6 | `GET /api/v1/dessertes?type_service=Nuit` | Trains de nuit uniquement | ✅ 200 |
| 7 | `GET /api/v1/dessertes?depart=Paris&arrivee=Berlin` | Desserte Paris → Berlin | ✅ 200 |
| 8 | `GET /api/v1/dessertes?type_service=INVALIDE` | Paramètre invalide | ✅ 422 |
| 9 | `GET /api/v1/comparisons/jour-vs-nuit` | Stats CO2 et durée par type | ✅ 200 |
| 10 | `GET /api/v1/comparisons/par-operateur` | Classement opérateurs | ✅ 200 |

---

## 7. Dashboard

Le dashboard est une application React (TypeScript) construite avec Vite. Il consomme l'API directement via fetch.

**Stack :** React 18, TypeScript, Vite, Tailwind CSS, Recharts

**3 pages :**

- **Vue Globale** : métriques clés (totaux), graphiques Recharts (répartition par pays, jour vs nuit, top opérateurs, CO2 comparatif)
- **Recherche** : formulaire de filtres (départ, arrivée, type_service, type_ligne, opérateur, pays) → tableau de résultats paginé
- **Données Brutes** : table complète de toutes les dessertes avec possibilité de tri

Le dashboard est déployé sur une Azure Web App séparée. En local il tourne sur le port 5173 (Vite dev server) et cible l'API sur `http://localhost:8000`.

---

## 8. Conformité RGPD

Le projet ne traite aucune donnée personnelle. Toutes les sources utilisées sont des données open data publiques (GTFS officiels des opérateurs ferroviaires, Open Night Train Database). Les informations stockées concernent uniquement des dessertes, des gares et des opérateurs — aucun utilisateur, aucun voyageur, aucune donnée nominative.

Malgré l'absence de données personnelles, les principes du RGPD ont été appliqués :

- **Transparence** : les sources de données sont documentées et traçables (colonne `source_donnee` dans chaque desserte)
- **Minimisation** : seules les données nécessaires à l'analyse sont collectées et stockées (pas de collecte excessive)
- **Sécurisation** : la base PostgreSQL est accessible uniquement via la `DATABASE_URL` stockée en variable d'environnement (jamais en clair dans le code), l'API est protégée par clé `X-API-Key`
- **Intégrité** : les scripts ETL garantissent la cohérence des données via les contraintes de clés étrangères en base

---

## 9. Déploiement Azure

L'infrastructure a été mise en place par mon binôme. Voici comment les composants s'articulent :

| Composant | Service Azure | Rôle |
|-----------|---------------|------|
| ETL | Azure Batch (pool Ubuntu 22.04, `Standard_D2s_v3`) | Exécution des scripts Python |
| Orchestration | Azure Data Factory | Trigger quotidien, pipeline Batch |
| Base de données | Azure Database for PostgreSQL Flexible | Stockage des données |
| API | Azure Web App (Python 3.12) | Exposition de l'API REST |
| Dashboard | Azure Web App (Node.js) | Serving du build React |

Le déclenchement quotidien fonctionne comme ça : ADF appelle le Batch Account, qui lance une tâche sur le pool. La tâche exécute `run_etl.sh` :

```bash
#!/bin/bash
cd /app
git pull origin main
python3 etl/orchestre.py
```

La configuration de la connexion PostgreSQL passe par la variable d'environnement `DATABASE_URL` (format SQLAlchemy), définie dans les paramètres de l'App Service et dans un fichier `.env` local pour le développement.

---

## 9. Difficultés rencontrées et solutions

### Azure Batch — package protégé au démarrage

**Problème :** Le start task du pool tentait d'installer des paquets apt, mais `nullboot` était protégé et bloquait toute l'installation.

**Solution :** Retirer complètement la partie `apt-get` du start task et passer par une image de base qui a déjà Python installé.

---

### Azure Batch — permissions sur /app

**Problème :** Le script n'arrivait pas à écrire dans `/app` lors du `git pull`.

**Solution :** Ajouter un `chmod 777 /app` dans le start task avant d'exécuter quoi que ce soit.

---

### ADF — "Can not access user batch account"

**Problème :** Le Linked Service ADF vers Batch retournait une erreur d'accès même avec les bonnes clés.

**Solution :** Il fallait d'abord lier un Storage Account au Batch Account dans Azure, puis activer la Managed Identity sur l'instance ADF et lui donner le rôle `Contributor` sur le Batch Account.

---

### Gares mal géocodées

**Problème :** En utilisant le pays de la source GTFS pour affecter le pays d'une gare, des gares belges apparaissaient côté France (Bruges classée FR parce que présente dans le GTFS SNCF TER).

**Solution :** Reverse geocoding par coordonnées GPS avec la bibliothèque `reverse_geocoder`. C'est un peu plus lent mais ça utilise les vraies frontières géographiques, pas la source du fichier.

---

### Fréquences hebdo toutes null

**Problème :** Après la jointure entre `trips.txt` et `calendar.txt` pour calculer les fréquences, tous les résultats étaient null. Après investigation, les `service_id` dans `trips.txt` étaient lus sans zéros de tête (`1`, `7`, `42`) alors que `calendar.txt` les avait avec zéros de tête (`000001`, `000007`).

**Solution :** Normalisation des deux côtés via la fonction `_norm_sid()` qui convertit en `int()` puis en `str()` pour retirer les zéros de tête.

---

### Opérateurs manquants (OCEdefault)

**Problème :** Les données SNCF contiennent un `agency_id` `OCEdefault` qui n'est pas un vrai opérateur mais une valeur de remplissage. Ça créait des opérateurs parasites en base.

**Solution :** Filtrage explicite de cet ID lors du transform des opérateurs. En cas de `agency_id` non résolu, on utilise le `operateur_defaut` défini par source (ex: `"SNCF"` pour sncf_ter).

---

## 10. Conclusion et perspectives

Ce projet m'a permis de mettre en pratique une vraie chaîne de données de bout en bout : collecte, transformation, stockage, exposition via API, visualisation. Les difficultés les plus intéressantes étaient sur l'ETL, notamment tout ce qui touche à la qualité des données GTFS (incohérences de typage, service_id avec zéros de tête, gares dupliquées entre pays).

Du côté Azure, c'était la première fois que je travaillais avec Azure Batch et ADF ensemble, et la configuration du Linked Service était franchement peu documentée pour notre cas d'usage.

**Ce qu'on pourrait améliorer :**
- Ajouter des trains internationaux (Eurostar, TGV Lyria, Thalys) qui sont absents du périmètre actuel
- Implémenter une recherche d'itinéraires avec correspondances (pas juste départ-arrivée direct)
- Mettre en place des alertes si l'ETL échoue (email ou Teams via Logic Apps)
- Ajouter des tests unitaires sur les fonctions de transform (haversine, norm_sid, etc.)
- Versionner les données pour suivre l'évolution dans le temps

La documentation Swagger générée automatiquement par FastAPI (`/docs`) complète cette documentation technique avec la liste exhaustive des paramètres et des schémas de réponse.
