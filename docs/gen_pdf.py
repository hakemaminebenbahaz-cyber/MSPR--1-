from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

doc = SimpleDocTemplate(
    'docs/documentation_technique.pdf',
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2*cm
)

styles = getSampleStyleSheet()
title_s  = ParagraphStyle('TT', parent=styles['Title'],   fontSize=20, spaceAfter=4,  textColor=colors.HexColor('#1a1a2e'), alignment=TA_CENTER)
sub_s    = ParagraphStyle('SS', parent=styles['Normal'],  fontSize=10, spaceAfter=6,  textColor=colors.HexColor('#666'),    alignment=TA_CENTER)
h1_s     = ParagraphStyle('H1', parent=styles['Heading1'],fontSize=13, spaceBefore=18,spaceAfter=6, textColor=colors.HexColor('#1a1a2e'))
h2_s     = ParagraphStyle('H2', parent=styles['Heading2'],fontSize=11, spaceBefore=12,spaceAfter=5, textColor=colors.HexColor('#2d4a8a'))
h3_s     = ParagraphStyle('H3', parent=styles['Heading3'],fontSize=10, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor('#444'))
body_s   = ParagraphStyle('BD', parent=styles['Normal'],  fontSize=9.5,leading=14,    spaceAfter=6, alignment=TA_JUSTIFY)
bullet_s = ParagraphStyle('BU', parent=styles['Normal'],  fontSize=9.5,leading=13,    spaceAfter=3, leftIndent=14)
code_s   = ParagraphStyle('CD', parent=styles['Code'],    fontSize=8,  leading=11,    spaceAfter=6, spaceBefore=4,
                           backColor=colors.HexColor('#f5f5f5'), leftIndent=10, rightIndent=10,
                           borderColor=colors.HexColor('#ddd'), borderWidth=1, borderPad=6)

def hr(): return HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#ccc'), spaceAfter=8)
def h1(t): return [Paragraph(t, h1_s), hr()]
def sp(): return Spacer(1, 0.2*cm)

content = []

# ── Titre
content.append(Spacer(1, 1*cm))
content.append(Paragraph('Documentation Technique', title_s))
content.append(Paragraph('ObRail Europe', title_s))
content.append(Spacer(1, 0.3*cm))
content.append(Paragraph('Projet MSPR — EPSI Bloc E6.1 RNCP36581', sub_s))
content.append(Paragraph('Etudiant : Hakem &nbsp;&nbsp;|&nbsp;&nbsp; Mars 2026', sub_s))
content.append(Spacer(1, 0.4*cm))
content.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#2d4a8a'), spaceAfter=18))

# ── 1. Présentation
content += h1('1. Presentation du projet')
content.append(Paragraph(
    "ObRail Europe est un projet de fin d'etudes realise dans le cadre du bloc E6.1 a l'EPSI. "
    "Le client fictif est un observatoire ferroviaire europeen qui souhaite centraliser les donnees "
    "de dessertes ferroviaires de plusieurs pays europeens, les rendre accessibles via une API et les "
    "visualiser dans un dashboard.", body_s))
content.append(Paragraph(
    "L'objectif : construire un pipeline complet allant de la collecte de donnees brutes "
    "(fichiers GTFS publics) jusqu'a une interface web, en passant par une base PostgreSQL sur Azure.", body_s))
content.append(Paragraph("Repartition du projet :", body_s))
content.append(Paragraph("- Hakem : scripts ETL (Extract/Transform/Load), API FastAPI, Dashboard React", bullet_s))
content.append(Paragraph("- Ami : infrastructure Azure (ADF, Azure Batch, PostgreSQL Azure, reseau)", bullet_s))

# ── 2. Architecture
content += h1('2. Architecture globale')
content.append(Paragraph("Flux de donnees :", body_s))
content.append(Paragraph("Sources GTFS / CSV  -->  ETL Python  -->  PostgreSQL Azure  -->  API FastAPI  -->  Dashboard React", code_s))
content.append(Paragraph(
    "Les scripts ETL tournent dans un pool Azure Batch (Ubuntu 22.04, Standard_D2s_v3). "
    "A chaque declenchement quotidien, ADF lance run_etl.sh qui fait un git pull "
    "puis execute le pipeline Python.", body_s))

# ── 3. Sources
content += h1('3. Sources de donnees')
content.append(Paragraph("Sources GTFS open data officielles + CSV trains de nuit :", body_s))
for src in [
    "SNCF TER (FR) : ~896 dessertes",
    "SNCF Intercites (FR) : ~47 dessertes",
    "DB Germany / Deutsche Bahn (DE) : ~89 dessertes",
    "SNCB Belgium (BE) : ~1047 dessertes",
    "OBB Austria (AT) : ~413 dessertes",
    "Open Night Train Database / Back-on-Track (multi-pays) : ~408 trains de nuit",
]:
    content.append(Paragraph("- " + src, bullet_s))
content.append(Paragraph("Total : environ 2 900 dessertes, 55 operateurs, 6 190 gares.", body_s))
content.append(Paragraph(
    "Le format GTFS (General Transit Feed Specification) est le standard utilise par la quasi-totalite "
    "des operateurs europeens. Chaque archive ZIP contient : agency.txt, stops.txt, routes.txt, "
    "trips.txt, stop_times.txt, calendar.txt, calendar_dates.txt.", body_s))
content.append(Paragraph(
    "Les emissions CO2 (g/km) sont issues du rapport EEA 2023 : "
    "France 14 g/km, Belgique 18 g/km, Allemagne 32 g/km, Autriche 12 g/km.", body_s))

# ── 4. ETL
content += h1('4. Pipeline ETL')
content.append(Paragraph('4.1 Extract', h2_s))
content.append(Paragraph(
    "Telechargement automatique des archives GTFS depuis les URLs officielles, decompression dans "
    "data/raw/<source>/. Pour l'Open Night Train Database : fichier CSV directement parse.", body_s))

content.append(Paragraph('4.2 Transform', h2_s))
content.append(Paragraph("Script principal : etl/transform/transform_gtfs.py → produit 3 CSV dans data/transformed/.", body_s))

content.append(Paragraph('Operateurs', h3_s))
content.append(Paragraph(
    "Lecture de agency.txt par source. Simplification des agency_id complexes (UUID). "
    "Filtrage des faux operateurs (OCEdefault). Fallback sur operateur_defaut si agency_id non resolu.", body_s))

content.append(Paragraph('Gares', h3_s))
content.append(Paragraph(
    "Probleme initial : pays_code base sur la source GTFS donnait des resultats faux "
    "(Bruges classee France car dans le fichier SNCF TER). "
    "Solution : reverse geocoding par coordonnees GPS (bibliotheque reverse_geocoder). "
    "Deduplication par cle (nom, pays_code).", body_s))

content.append(Paragraph('Dessertes', h3_s))
for step in [
    "Filtrage routes ferroviaires (route_type 2, 100-107)",
    "Identification premier/dernier arret via stop_times.txt",
    "Deduplication par (route_id, direction_id) — trip le plus long conserve",
    "Calcul distance haversine entre coordonnees GPS des gares",
    "Calcul frequence hebdomadaire : calendar.txt (somme lundi-dimanche) ou calendar_dates.txt (dates actives / semaines)",
    "Typage automatique : Grande vitesse / Intercite / Train regional / Train de nuit interne",
]:
    content.append(Paragraph("- " + step, bullet_s))

content.append(Paragraph('4.3 Load', h2_s))
content.append(Paragraph(
    "Insertion dans PostgreSQL via SQLAlchemy. Ordre : operateurs → gares → dessertes (respect des FK). "
    "Resolution des FK par correspondance de noms avant insertion.", body_s))

# ── 5. BDD
content += h1('5. Base de donnees')
content.append(Paragraph("PostgreSQL sur Azure Database for PostgreSQL Flexible Server. Trois tables :", body_s))

content.append(Paragraph('Table operateurs', h3_s))
for col in ["id — SERIAL PK", "nom — VARCHAR(100)", "pays_code — CHAR(2)"]:
    content.append(Paragraph("- " + col, bullet_s))

content.append(Paragraph('Table gares', h3_s))
for col in ["id — SERIAL PK", "nom — VARCHAR(150)", "pays_code — CHAR(2)", "latitude, longitude — NUMERIC(9,6)"]:
    content.append(Paragraph("- " + col, bullet_s))

content.append(Paragraph('Table dessertes', h3_s))
for col in [
    "id — VARCHAR(20) PK (ex: FR_ROUTE01_0)",
    "operateur_id — INT FK -> operateurs.id",
    "nom_ligne — VARCHAR(200)",
    "type_ligne — Grande vitesse / Intercite / Train regional / Train de nuit interne",
    "type_service — Jour / Nuit",
    "gare_depart_id, gare_arrivee_id — INT FK -> gares.id",
    "heure_depart, heure_arrivee — TIME",
    "distance_km — INT (haversine)",
    "duree_h — NUMERIC(5,2)",
    "emissions_co2_gkm — NUMERIC(6,2) — source EEA 2023",
    "frequence_hebdo — INT (jours/semaine, 1 a 7)",
    "traction — VARCHAR(20)",
    "source_donnee — VARCHAR(100)",
]:
    content.append(Paragraph("- " + col, bullet_s))

# ── 6. API
content += h1('6. API REST')
content.append(Paragraph(
    "Stack : Python 3.12, FastAPI, SQLAlchemy ORM, psycopg2-binary, Pydantic v2. "
    "Deployee sur Azure Web App port 8000. Documentation Swagger sur /docs.", body_s))

content.append(Paragraph('Authentification', h3_s))
content.append(Paragraph("Tous les endpoints /api/v1/ requierent le header X-API-Key.", body_s))
content.append(Paragraph("X-API-Key: <votre_cle>", code_s))

content.append(Paragraph('Endpoints', h3_s))
for ep in [
    "GET /health — etat de l'API",
    "GET /api/v1/operateurs/ — liste (filtre pays_code)",
    "GET /api/v1/gares/ — liste (filtres nom, pays_code)",
    "GET /api/v1/dessertes/ — filtres : depart, arrivee, type_service, type_ligne, operateur, pays_code, skip, limit",
    "GET /api/v1/dessertes/{id} — detail avec FK resolues",
    "GET /api/v1/comparisons/stats-globales — totaux",
    "GET /api/v1/comparisons/jour-vs-nuit — CO2 et duree par type",
    "GET /api/v1/comparisons/par-pays — dessertes par pays",
    "GET /api/v1/comparisons/par-operateur — classement operateurs",
]:
    content.append(Paragraph("- " + ep, bullet_s))

content.append(Paragraph('Exemple de reponse — GET /api/v1/dessertes/?depart=Paris&arrivee=Bruxelles', h3_s))
content.append(Paragraph(
    '[{ "id": "FR_ROUTE42_0", "nom_ligne": "Paris Nord - Bruxelles Midi",\n'
    '   "type_service": "Jour", "distance_km": 312, "frequence_hebdo": 7,\n'
    '   "gare_depart": {"nom": "Paris Nord", "pays_code": "FR"},\n'
    '   "gare_arrivee": {"nom": "Bruxelles Midi", "pays_code": "BE"} }]', code_s))

content.append(Paragraph('Tests API (Postman)', h3_s))
content.append(Paragraph(
    "La collection complete est disponible dans docs/ObRail_API_Postman.json. "
    "Voici les principaux cas de test executes :", body_s))

test_data = [
    ['Requete', 'Resultat attendu', 'Code'],
    ['GET /health', 'status: ok, database: connected', '200'],
    ['GET /api/v1/gares?pays_code=FR', 'Gares francaises uniquement', '200'],
    ['GET /api/v1/gares/99999', 'Gare inexistante', '404'],
    ['GET /api/v1/operateurs?pays_code=FR', 'SNCF, SNCF VOYAGEURS', '200'],
    ['GET /api/v1/dessertes?type_service=Nuit', 'Trains de nuit uniquement', '200'],
    ['GET /api/v1/dessertes?depart=Paris&arrivee=Berlin', 'Desserte Paris->Berlin', '200'],
    ['GET /api/v1/dessertes?type_service=INVALIDE', 'Parametre invalide', '422'],
    ['GET /api/v1/comparisons/jour-vs-nuit', 'Stats CO2 et duree', '200'],
    ['GET /api/v1/comparisons/par-operateur', 'Classement operateurs', '200'],
]
t = Table(test_data, colWidths=[7*cm, 7*cm, 2*cm])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d4a8a')),
    ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
    ('FONTSIZE',   (0,0), (-1,0), 8),
    ('FONTSIZE',   (0,1), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
    ('ALIGN', (2,0), (2,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
content.append(t)

# ── 7. Dashboard
content += h1('7. Dashboard')
content.append(Paragraph(
    "Application React TypeScript (Vite), consommant l'API via fetch. "
    "Deployee sur Azure Web App. Stack : React 18, TypeScript, Vite, Tailwind CSS, Recharts.", body_s))
for p in [
    "Vue Globale : metriques cles, graphiques (repartition par pays, jour vs nuit, top operateurs, CO2 comparatif)",
    "Recherche : formulaire de filtres (depart, arrivee, type_service, type_ligne, operateur, pays) + resultats",
    "Donnees Brutes : table complete avec noms d'operateurs et de gares resolus",
]:
    content.append(Paragraph("- " + p, bullet_s))

# ── 8. RGPD
content += h1('8. Conformite RGPD')
content.append(Paragraph(
    "Le projet ne traite aucune donnee personnelle. Toutes les sources sont des donnees open data publiques "
    "(GTFS officiels des operateurs, Open Night Train Database). Aucun utilisateur ni voyageur "
    "n'est identifiable dans les donnees stockees.", body_s))
content.append(Paragraph("Mesures appliquees :", body_s))
for m in [
    "Transparence : sources documentees et tracables via la colonne source_donnee de chaque desserte",
    "Minimisation : seules les donnees necessaires a l'analyse sont collectees",
    "Securisation : DATABASE_URL en variable d'environnement (jamais en clair dans le code), API protegee par X-API-Key",
    "Integrite : contraintes de cles etrangeres en base garantissant la coherence des donnees",
]:
    content.append(Paragraph("- " + m, bullet_s))

# ── 9. Déploiement
content += h1('9. Deploiement Azure')
for comp in [
    "Azure Batch (pool Ubuntu 22.04, Standard_D2s_v3) : execution des scripts ETL Python",
    "Azure Data Factory : orchestration, trigger quotidien, Custom Activity Batch",
    "Azure Database for PostgreSQL Flexible Server : stockage des donnees",
    "Azure Web App Python 3.12 : hebergement de l'API FastAPI",
    "Azure Web App Node.js : serving du build React (dashboard)",
]:
    content.append(Paragraph("- " + comp, bullet_s))
content.append(Paragraph(
    "A chaque declenchement, ADF envoie une tache au Batch Account qui execute run_etl.sh. "
    "Ce script fait un git pull puis lance python3 etl/orchestre.py. "
    "La DATABASE_URL est injectee via variable d'environnement dans l'App Service.", body_s))

doc.build(content)
print("PDF genere : docs/documentation_technique.pdf")
