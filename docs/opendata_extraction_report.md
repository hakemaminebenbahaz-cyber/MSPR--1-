# Rapport d'Extraction - Donnees Ouvertes

Date d'extraction: 2026-03-05 00:50:29

## Sources extraites

### back_on_track_night_trains.csv
- Lignes: 3
- Colonnes: nom, operateur, depart, arrivee, distance_km, duree_h, gares_intermediaires, type, source

### eurostat_rail_transport.csv
- Lignes: 6
- Colonnes: pays, trains_nuit_2023, trains_jour_2023, passagers_ferroviaires_millions, emissions_co2_evitees_tonnes

### sncf_stations_data.csv
- Lignes: 4
- Colonnes: code_uic, nom_gare, ville, region, voyageurs_2022, type_trains

## Utilisation pour le projet ObRail

Ces donnees seront utilisees pour:
1. Completer les informations sur les trains de nuit
2. Ajouter des statistiques par pays
3. Enrichir les donnees GTFS avec des metadonnees
