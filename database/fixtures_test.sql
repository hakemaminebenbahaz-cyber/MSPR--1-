-- Données de test minimales pour le CI/CD

INSERT INTO operateurs (id, nom, pays_code) VALUES
  (1, 'SNCF', 'FR'),
  (2, 'Deutsche Bahn', 'DE'),
  (3, 'Trenitalia', 'IT');

INSERT INTO gares (id, nom, ville, pays_code, latitude, longitude) VALUES
  (1, 'Paris Gare de Lyon', 'Paris', 'FR', 48.8448, 2.3735),
  (2, 'Lyon Part-Dieu', 'Lyon', 'FR', 45.7606, 4.8596),
  (3, 'Berlin Hauptbahnhof', 'Berlin', 'DE', 52.5251, 13.3694),
  (4, 'Roma Termini', 'Roma', 'IT', 41.9009, 12.5009);

INSERT INTO dessertes (id, operateur_id, nom_ligne, type_ligne, type_service, gare_depart_id, gare_arrivee_id, heure_depart, heure_arrivee, distance_km, duree_h, emissions_co2_gkm, frequence_hebdo, traction, source_donnee) VALUES
  ('SNCF_001', 1, 'Paris-Lyon TGV', 'Train grande vitesse', 'Jour', 1, 2, '08:00:00', '10:00:00', 392, 2.0, 3.0, 14, 'électrique', 'test'),
  ('SNCF_002', 1, 'Paris-Lyon Nuit', 'Train de nuit', 'Nuit', 1, 2, '22:00:00', '06:00:00', 392, 8.0, 3.0, 7, 'électrique', 'test'),
  ('DB_001', 2, 'Berlin-Munich ICE', 'Train grande vitesse', 'Jour', 3, 1, '07:00:00', '11:30:00', 585, 4.5, 28.0, 14, 'électrique', 'test');
