# Rapport de Scraping Web - Projet ObRail

Date du scraping: 2025-12-04 11:34:45

## Sources scrapées

| Source | Fichier | Enregistrements |
|--------|---------|-----------------|
| all_scraped_data_merged | all_scraped_data_merged.csv | 9 |
| railcc_train_routes | railcc_train_routes.csv | 4 |
| wikipedia_european_railways | wikipedia_european_railways.csv | 5 |

**Total: 18 enregistrements**

## Détail par source

### all_scraped_data_merged.csv
- Enregistrements: 9
- Colonnes: from_city, to_city, distance_km, duration_h, changes, price_eur, train_types, website_source, scraped_date, route_id, data_source_file, country, rail_network_km, high_speed_km, main_operator, passengers_per_year_millions, night_trains_count, source, night_train_ratio

### railcc_train_routes.csv
- Enregistrements: 4
- Colonnes: from_city, to_city, distance_km, duration_h, changes, price_eur, train_types, website_source, scraped_date, route_id

### wikipedia_european_railways.csv
- Enregistrements: 5
- Colonnes: country, rail_network_km, high_speed_km, main_operator, passengers_per_year_millions, night_trains_count, source, scraped_date, night_train_ratio

## Utilisation pour l'analyse

Ces données complètent les données GTFS avec:
1. Informations détaillées sur les trains de nuit
2. Statistiques par pays sur les réseaux ferroviaires
3. Itinéraires et prix des trains
4. Métadonnées sur les opérateurs
