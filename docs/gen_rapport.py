from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

OUTPUT = "docs/rapport_projet.pdf"

NAVY  = colors.HexColor("#1e2a4a")
BLUE  = colors.HexColor("#2563eb")
LIGHT = colors.HexColor("#f1f5f9")
GRAY  = colors.HexColor("#64748b")
GREEN = colors.HexColor("#16a34a")
WHITE = colors.white

PAGE_W = 15.5 * cm   # largeur utile (A4 - marges)

def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm,  bottomMargin=2.5*cm,
    )

    # ── styles ──────────────────────────────────────────────
    title_s    = ParagraphStyle("T",  fontName="Helvetica-Bold",   fontSize=24, textColor=NAVY, alignment=TA_CENTER, spaceAfter=6)
    sub_s      = ParagraphStyle("S",  fontName="Helvetica",        fontSize=12, textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)
    h1_s       = ParagraphStyle("H1", fontName="Helvetica-Bold",   fontSize=15, textColor=NAVY, spaceBefore=16, spaceAfter=8)
    h2_s       = ParagraphStyle("H2", fontName="Helvetica-Bold",   fontSize=12, textColor=BLUE, spaceBefore=10, spaceAfter=6)
    body_s     = ParagraphStyle("B",  fontName="Helvetica",        fontSize=10, leading=15, spaceAfter=8, alignment=TA_JUSTIFY)
    bullet_s   = ParagraphStyle("BU", fontName="Helvetica",        fontSize=10, leading=15, spaceAfter=4, leftIndent=16)
    cell_h_s   = ParagraphStyle("CH", fontName="Helvetica-Bold",   fontSize=9,  textColor=WHITE, leading=13)
    cell_s     = ParagraphStyle("C",  fontName="Helvetica",        fontSize=9,  leading=13)
    cell_grn_s = ParagraphStyle("CG", fontName="Helvetica-Bold",   fontSize=9,  textColor=GREEN, leading=13)

    # ── helpers ──────────────────────────────────────────────
    def h1(text):
        return [HRFlowable(width="100%", thickness=2, color=NAVY),
                Spacer(1, 3), Paragraph(text, h1_s)]

    def h2(text):   return [Paragraph(text, h2_s)]
    def p(text):    return [Paragraph(text, body_s)]
    def b(text):    return [Paragraph(f"• {text}", bullet_s)]
    def sp(n=1):    return Spacer(1, n*0.4*cm)

    def c(text, style=None):
        return Paragraph(text, style or cell_s)

    def ch(text):   return Paragraph(text, cell_h_s)
    def cg(text):   return Paragraph(text, cell_grn_s)

    def table_style():
        return TableStyle([
            ("BACKGROUND",   (0, 0), (-1,  0), NAVY),
            ("ROWBACKGROUNDS",(0, 1),(-1, -1), [WHITE, LIGHT]),
            ("BOX",          (0, 0), (-1, -1), 0.5, NAVY),
            ("INNERGRID",    (0, 0), (-1, -1), 0.3, GRAY),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])

    def img(filename, width=PAGE_W, height=8*cm):
        path = os.path.join("docs", "screenshots", filename)
        if os.path.exists(path):
            return [Image(path, width=width, height=height), Spacer(1, 0.3*cm)]
        return []

    story = []

    # ════════════════════════════════════════════════════════
    # PAGE DE TITRE
    # ════════════════════════════════════════════════════════
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("ObRail Europe", title_s))
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph("Rapport de Projet", sub_s))
    story.append(Paragraph("BENBAHAZ Hakem - HALIBA Jihad - BELLIL Samy - MOHANRAJU Serenic", sub_s))
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="60%", thickness=2, color=BLUE, hAlign="CENTER"))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("", sub_s))
    story.append(PageBreak())

    # ════════════════════════════════════════════════════════
    # 1. INTRODUCTION
    # ════════════════════════════════════════════════════════
    story += h1("1. Introduction")
    story += p(
        "Ce rapport présente le travail réalisé dans le cadre de la MSPR TPRE512, "
        "pour le client fictif <b>ObRail Europe</b>: un observatoire ferroviaire "
        "européen qui veut centraliser et analyser les données ferroviaires de "
        "plusieurs pays."
    )
    story += p(
        "L'objectif est de construire un pipeline ETL complet (Extract, Transform, Load), "
        "une base de données, une API REST et un tableau de bord: le tout déployé sur "
        "Azure et reproductible par n'importe quel développeur."
    )
    story += p(
        "On a travaillé sur des données réelles Open Data : des fichiers GTFS officiels "
        "publiés par les opérateurs ferroviaires européens eux-mêmes. Ce sont de vraies "
        "données de trains, pas des données de test."
    )
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 2. CONTEXTE ET BESOIN CLIENT
    # ════════════════════════════════════════════════════════
    story += h1("2. Contexte et besoin client")
    story += p(
        "ObRail Europe veut avoir une vue d'ensemble sur les réseaux ferroviaires européens. "
        "Concrètement, voici ce qu'ils nous ont demandé :"
    )
    for item in [
        "Centraliser les données de plusieurs pays dans une seule base",
        "Automatiser la collecte quotidienne des données",
        "Exposer les données via une API documentée",
        "Visualiser tout ça dans un tableau de bord",
        "S'assurer de la qualité des données collectées",
    ]:
        story += b(item)
    story.append(sp())
    story += p(
        "Pour répondre à ça, on a choisi Python pour l'ETL, PostgreSQL pour le stockage, "
        "FastAPI pour l'API, React pour le dashboard, et Azure pour tout déployer."
    )

    # ════════════════════════════════════════════════════════
    # 3. SOURCES DE DONNÉES
    # ════════════════════════════════════════════════════════
    story += h1("3. Sources de données et justification des choix")
    story += p(
        "Le choix des sources a été guidé par trois critères : disponibilité en Open Data, "
        "format standardisé, et couverture géographique européenne."
    )

    story += h2("3.1 Données GTFS")
    story += p(
        "Le format GTFS (General Transit Feed Specification) est le standard mondial pour "
        "les données de transport, créé par Google et adopté par la quasi-totalité des "
        "opérateurs ferroviaires européens. Il garantit une structure homogène entre pays, "
        "ce qui simplifie beaucoup la normalisation dans l'ETL."
    )

    gtfs_rows = [
        [ch("Pays"), ch("Opérateur"), ch("Source"), ch("Justification")],
        [c("France"),   c("SNCF"), c("transport.data.gouv.fr"), c("Source officielle, MAJ hebdomadaire")],
        [c("Allemagne"),c("DB"),   c("gtfs.de"),                c("Standard DB officiel, réseau complet")],
        [c("Autriche"), c("ÖBB"),  c("data.oebb.at"),           c("Open Data officiel ÖBB")],
        [c("Suisse"),   c("SBB"),  c("opentransportdata.swiss"),c("Plateforme nationale suisse")],
        [c("Belgique"), c("SNCB"), c("data.infrabel.be"),       c("Open Data infrastructure belge")],
    ]
    t = Table(gtfs_rows, colWidths=[2.8*cm, 2.8*cm, 5*cm, 4.9*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    story += h2("3.2 Données CO2")
    story += p(
        "Les émissions CO2 viennent de l'Agence Européenne de l'Environnement (EEA). "
        "C'est la référence officielle européenne pour les données environnementales, "
        "publiques et régulièrement mises à jour. Elles nous permettent de calculer "
        "l'impact carbone par type de train et par pays."
    )

    story += h2("3.3 Web Scraping Wikipedia")
    story += p(
        "Pour enrichir le contexte ferroviaire de chaque pays (longueur du réseau, "
        "km de grande vitesse, taux d'électrification), on a mis en place un scraping "
        "des pages Wikipedia dédiées. C'est la seule source gratuite et structurée "
        "qui agrège ces informations de manière comparative entre pays. "
        "Les données sont extraites via BeautifulSoup et stockées en CSV."
    )

    story += h2("3.4 Trains de nuit")
    story += p(
        "Un fichier CSV recense les trains de nuit européens. Il complète les données "
        "GTFS qui ne distinguent pas toujours les services de nuit, et permet d'enrichir "
        "le champ type_service (Jour/Nuit) dans la base."
    )

    # ════════════════════════════════════════════════════════
    # 4. ARCHITECTURE TECHNIQUE
    # ════════════════════════════════════════════════════════
    story += h1("4. Architecture technique")
    story += p(
        "Le projet est organisé en couches indépendantes. Chaque couche peut évoluer "
        "sans toucher aux autres: c'est un principe de base pour la maintenabilité."
    )

    arch_rows = [
        [ch("Couche"), ch("Technologie"), ch("Rôle")],
        [c("Extraction"),    c("Python, requests, BeautifulSoup"), c("Téléchargement et scraping")],
        [c("Transformation"),c("Python, pandas"),                  c("Nettoyage, normalisation, enrichissement")],
        [c("Stockage"),      c("PostgreSQL Azure"),                c("Base relationnelle centralisée")],
        [c("API"),           c("FastAPI, SQLAlchemy"),             c("REST documentée via Swagger")],
        [c("Dashboard"),     c("React, TypeScript, Recharts"),     c("Tableau de bord interactif")],
        [c("Orchestration"), c("Azure Data Factory + Batch"),      c("Automatisation quotidienne")],
        [c("Déploiement"),   c("Azure Web App"),                   c("API accessible en ligne")],
    ]
    t = Table(arch_rows, colWidths=[3.5*cm, 6*cm, 6*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 5. PIPELINE ETL
    # ════════════════════════════════════════════════════════
    story += h1("5. Pipeline ETL")

    story += h2("5.1 Extraction")
    for item in [
        "<b>extract_gtfs.py</b>: télécharge et dézippe les fichiers GTFS de chaque opérateur",
        "<b>extract_opendata.py</b>: récupère les données CO2 et trains de nuit",
        "<b>extract_scraping.py</b>: scrape Wikipedia pour le contexte ferroviaire européen",
    ]:
        story += b(item)
    story += p(
        "Chaque script est autonome et peut être relancé seul. Les fichiers bruts "
        "sont dans data/raw/ et ne sont pas versionnés (trop volumineux)."
    )

    story += h2("5.2 Transformation")
    story += p("C'est la phase la plus complexe. Les étapes principales :")
    for item in [
        "<b>Normalisation des service_id</b>: certains fichiers GTFS ont des zéros en tête ('001' vs '1'). La fonction _norm_sid() harmonise ça.",
        "<b>Fréquence hebdomadaire</b>: on calcule le maximum sur tous les trajets d'une ligne avant déduplication, pour ne pas perdre les lignes fréquentes.",
        "<b>Détection du pays par GPS</b>: les gares sont géolocalisées et leur pays est déterminé par bounding boxes via reverse_geocoder.",
        "<b>Déduplication par priorité</b>: les sources nationales ont priorité sur les sources génériques.",
        "<b>Enrichissement CO2</b>: chaque desserte reçoit les émissions CO2 selon son type de traction et son pays.",
        "<b>Classification Jour/Nuit</b>: le type de service est déterminé en croisant les horaires GTFS avec la liste des trains de nuit.",
    ]:
        story += b(item)

    story += h2("5.3 Chargement")
    story += p(
        "load_to_postgresql.py insère les données dans PostgreSQL Azure via SQLAlchemy "
        "avec une stratégie d'upsert (INSERT ON CONFLICT) pour éviter les doublons "
        "lors des relances quotidiennes. Connexion chiffrée SSL, credentials dans .env."
    )

    story += h2("5.4 Orchestration")
    story += p(
        "orchestre.py appelle les trois phases dans l'ordre. Il est déclenché "
        "quotidiennement par Azure Data Factory. L'exécution se fait sur un pool "
        "de nœuds Azure Batch via le script run_etl.sh."
    )

    # ════════════════════════════════════════════════════════
    # 6. BASE DE DONNÉES
    # ════════════════════════════════════════════════════════
    story += h1("6. Base de données")

    story += h2("6.1 Pourquoi PostgreSQL ?")
    story += p(
        "On a choisi PostgreSQL parce que nos données sont relationnelles : "
        "les dessertes référencent des gares et des opérateurs. Les clés étrangères "
        "garantissent l'intégrité. PostgreSQL est aussi disponible nativement sur Azure "
        "avec SSL, et c'est open source: pas de coût de licence."
    )
    story += p(
        "Une base NoSQL aurait eu du sens si les données étaient non structurées "
        "ou très variables. Ce n'est pas le cas avec le format GTFS qui est très homogène."
    )

    story += h2("6.2 Schéma des tables")

    schema_rows = [
        [ch("Table"), ch("Colonnes principales"), ch("Rôle")],
        [c("operateurs"),
         c("id, nom, pays_code, type_operateur"),
         c("Référentiel des compagnies ferroviaires")],
        [c("gares"),
         c("id, nom, pays_code, latitude, longitude"),
         c("Référentiel des gares européennes")],
        [c("dessertes"),
         c("id, nom_ligne, gare_depart_id, gare_arrivee_id,\noperateur_id, distance_km, duree_h,\nfrequence_hebdo, type_service, emissions_co2_gkm"),
         c("Table centrale des liaisons ferroviaires")],
    ]
    t = Table(schema_rows, colWidths=[3*cm, 7*cm, 5.5*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 7. API REST
    # ════════════════════════════════════════════════════════
    story += h1("7. API REST")

    story += h2("7.1 Pourquoi FastAPI ?")
    for item in [
        "Documentation Swagger générée automatiquement: très pratique pour la démo",
        "Validation des données via Pydantic v2",
        "Performances asynchrones (ASGI)",
        "Intégration naturelle avec SQLAlchemy",
        "Même langage que l'ETL (Python): cohérence du projet",
    ]:
        story += b(item)

    story += h2("7.2 Endpoints principaux")
    ep_rows = [
        [ch("Endpoint"), ch("Description")],
        [c("GET /api/v1/gares"),                          c("Liste des gares avec filtres")],
        [c("GET /api/v1/operateurs"),                     c("Liste des opérateurs par pays")],
        [c("GET /api/v1/dessertes"),                      c("Dessertes avec filtres départ/arrivée/type")],
        [c("GET /comparisons/stats-globales"),            c("Statistiques générales")],
        [c("GET /comparisons/co2-par-type"),              c("Émissions CO2 par type de train")],
        [c("GET /comparisons/repartition-jour-nuit"),     c("Répartition Jour / Nuit")],
        [c("GET /comparisons/qualite-donnees"),           c("Taux de valeurs manquantes par table")],
        [c("GET /comparisons/contexte-pays"),             c("Contexte ferroviaire européen par pays")],
    ]
    t = Table(ep_rows, colWidths=[8*cm, 7.5*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    story += h2("7.3 Déploiement")
    story += p(
        "L'API est déployée sur Azure Web App (Python 3.12). La documentation Swagger "
        "est accessible sur /docs. Les credentials sont dans les variables d'environnement "
        "Azure App Service: jamais dans le code."
    )

    story += h2("7.4 Tests des endpoints")
    tests_rows = [
        [ch("Endpoint testé"), ch("Résultat attendu"), ch("Statut")],
        [c("GET /api/v1/gares"),                      c("Liste JSON des gares"),         cg("✓ 200 OK")],
        [c("GET /api/v1/operateurs"),                 c("Liste JSON des opérateurs"),    cg("✓ 200 OK")],
        [c("GET /api/v1/dessertes"),                  c("Liste JSON des dessertes"),     cg("✓ 200 OK")],
        [c("GET /comparisons/stats-globales"),        c("Objet JSON avec compteurs"),    cg("✓ 200 OK")],
        [c("GET /comparisons/co2-par-type"),          c("Liste CO2 par type"),           cg("✓ 200 OK")],
        [c("GET /comparisons/repartition-jour-nuit"), c("Répartition Jour/Nuit"),        cg("✓ 200 OK")],
        [c("GET /comparisons/qualite-donnees"),       c("Taux manquants par table"),     cg("✓ 200 OK")],
        [c("GET /comparisons/contexte-pays"),         c("Contexte par pays"),            cg("✓ 200 OK")],
    ]
    t = Table(tests_rows, colWidths=[7.5*cm, 5.5*cm, 2.5*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 8. DASHBOARD
    # ════════════════════════════════════════════════════════
    story += h1("8. Tableau de bord")

    story += h2("8.1 Choix techniques")
    story += p(
        "On a choisi React + TypeScript pour la robustesse du typage, Vite pour le build, "
        "Tailwind CSS pour le design, et Recharts pour les graphiques. C'est une stack "
        "moderne qu'on maîtrise et qui nous a permis d'avancer vite."
    )

    story += h2("8.2 Vue Globale")
    story += p(
        "La page principale affiche les indicateurs clés : 55 opérateurs, 6 190 gares, "
        "2 203 trains de jour et 650 trains de nuit. On y trouve les graphiques de "
        "répartition Jour/Nuit, les émissions CO2 par type de service et la répartition "
        "par type de ligne."
    )
    story += img("screen1_vue_globale.png.png", width=PAGE_W, height=9*cm)

    story += p(
        "En bas de page : le contexte ferroviaire européen (données Wikipedia croisées "
        "avec nos GTFS) et la qualité des données avec le taux de complétude champ par champ."
    )
    story += img("screen2_contexte_qualite.png.png", width=PAGE_W, height=9*cm)

    story += h2("8.3 Carte des gares")
    story += p(
        "Une carte interactive affiche les 6 059 gares géolocalisées, colorées par pays. "
        "On survole un point pour voir le nom de la gare."
    )
    story += img("screen3_carte.png.png", width=PAGE_W, height=9*cm)

    story += h2("8.4 Page Recherche")
    story += p(
        "On peut filtrer par gare de départ, gare d'arrivée, type Jour/Nuit et "
        "catégorie de ligne. Il y a aussi une recherche de gares et d'opérateurs."
    )
    story += img("screen4_recherche.png.png", width=PAGE_W, height=9*cm)

    story += h2("8.5 Accessibilité numérique")
    story += p(
        "On a ajouté des attributs ARIA sur tous les graphiques et barres de progression. "
        "Un malvoyant utilisant un lecteur d'écran entendra le contenu des graphiques "
        "au lieu de silence. Les contrastes respectent WCAG 2.1 niveau AA."
    )

    # ════════════════════════════════════════════════════════
    # 9. DÉPLOIEMENT AZURE
    # ════════════════════════════════════════════════════════
    story += h1("9. Déploiement Azure")

    azure_rows = [
        [ch("Service Azure"), ch("Usage")],
        [c("Azure PostgreSQL Flexible Server"), c("Base de données de production avec SSL")],
        [c("Azure Batch"),                      c("Exécution des scripts ETL sur pool de nœuds")],
        [c("Azure Data Factory"),               c("Orchestration et trigger quotidien du pipeline")],
        [c("Azure Web App"),                    c("Hébergement de l'API FastAPI (Python 3.12)")],
        [c("Azure Blob Storage"),               c("Stockage des fichiers GTFS bruts")],
    ]
    t = Table(azure_rows, colWidths=[7*cm, 8.5*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 10. RGPD ET SÉCURITÉ
    # ════════════════════════════════════════════════════════
    story += h1("10. RGPD et sécurité des données")
    story += p(
        "Les données utilisées sont des données publiques Open Data: pas de données "
        "personnelles. Mais on a quand même appliqué les bonnes pratiques de sécurité :"
    )
    for item in [
        "Credentials dans des variables d'environnement (.env), jamais dans le code",
        "Le fichier .env est exclu du versioning Git (.gitignore)",
        "Connexion PostgreSQL Azure chiffrée via SSL",
        "CORS configurés pour n'autoriser que les origines connues",
        "L'API est en lecture seule: pas de stockage de données utilisateur",
        "Données GTFS sous licence ouverte",
    ]:
        story += b(item)
    story += p(
        "Si on ajoutait des comptes utilisateurs, il faudrait une authentification JWT, "
        "un consentement explicite et une politique de rétention conforme au RGPD."
    )

    # ════════════════════════════════════════════════════════
    # 11. QUALITÉ DES DONNÉES
    # ════════════════════════════════════════════════════════
    story += h1("11. Qualité des données")
    for item in [
        "<b>Déduplication</b>: les doublons entre sources sont éliminés par priorité (national > générique)",
        "<b>Validation des formats</b>: les noms invalides ('-', vides, trop courts) sont filtrés",
        "<b>Normalisation des IDs</b>: les service_id GTFS sont harmonisés entre fichiers",
        "<b>Corrections manuelles</b>: les pays incorrects sur certains opérateurs ont été corrigés par ID",
        "<b>Monitoring dans le dashboard</b>: taux de valeurs manquantes visible en temps réel",
    ]:
        story += b(item)
    story.append(sp())

    q_rows = [
        [ch("Table"), ch("Champs surveillés"), ch("Complétude")],
        [c("operateurs"), c("nom, pays_code, type_operateur"),              c("> 98%")],
        [c("gares"),      c("nom, pays_code, latitude, longitude"),         c("> 95%")],
        [c("dessertes"),  c("nom_ligne, operateur, frequence_hebdo, co2"),  c("> 90%")],
    ]
    t = Table(q_rows, colWidths=[3.5*cm, 8*cm, 4*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 12. PERSPECTIVES IA
    # ════════════════════════════════════════════════════════
    story += h1("12. Perspectives IA")
    story += p(
        "Les données produites par ce pipeline sont prêtes à être utilisées "
        "pour entraîner des modèles de Machine Learning :"
    )
    ia_rows = [
        [ch("Objectif"), ch("Features"), ch("Modèle envisagé")],
        [c("Prédire la fréquence hebdomadaire"),
         c("type_ligne, distance_km, pays_code, traction"),
         c("Random Forest / XGBoost")],
        [c("Prédire les émissions CO2"),
         c("distance_km, duree_h, type_ligne, traction"),
         c("Régression linéaire")],
        [c("Détecter les anomalies"),
         c("frequence_hebdo, emissions_co2_gkm, distance_km"),
         c("Isolation Forest")],
    ]
    t = Table(ia_rows, colWidths=[5*cm, 6.5*cm, 4*cm])
    t.setStyle(table_style())
    story.append(t)
    story.append(sp())

    # ════════════════════════════════════════════════════════
    # 14. CONCLUSION
    # ════════════════════════════════════════════════════════
    story += h1("13. Conclusion")
    story += p(
        "Ce projet nous a permis de construire un pipeline ETL complet de bout en bout, "
        "sur des données ferroviaires européennes réelles. De l'extraction des fichiers "
        "GTFS officiels jusqu'au tableau de bord interactif, en passant par l'API REST "
        "déployée sur Azure, chaque partie a été pensée pour être maintenable."
    )
    story += p(
        "Les problèmes rencontrés: normalisation des IDs GTFS, gestion des doublons, "
        "déploiement Azure: ont été de bonnes occasions d'apprendre comment ça se passe "
        "sur un vrai projet de données."
    )
    story += p(
        "Le projet est entièrement reproductible : le README permet à n'importe quel "
        "développeur de relancer l'ETL, l'API et le dashboard en local via Docker Compose. "
        "Les données sont prêtes pour alimenter un futur modèle de Machine Learning."
    )

    doc.build(story)
    print(f"Rapport généré : {OUTPUT}")

if __name__ == "__main__":
    build()
