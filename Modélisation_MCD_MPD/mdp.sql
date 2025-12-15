TABLE gares (
    stop_id VARCHAR(50) PRIMARY KEY,
    stop_code VARCHAR(20),
    stop_name VARCHAR(200),
    stop_name_clean VARCHAR(200),
    stop_lat DECIMAL(10, 6),
    stop_lon DECIMAL(10, 6),
    zone_id VARCHAR(20),
    parent_station VARCHAR(50),
    station_code VARCHAR(50),
    pays VARCHAR(3),
    source VARCHAR(50),
    processed_date DATE
);

INDEX idx_gares_pays ON gares(pays);
INDEX idx_gares_station_code ON gares(station_code);

TABLE lignes (
    route_id VARCHAR(50) PRIMARY KEY,
    agency_id VARCHAR(50),
    route_short_name VARCHAR(50),
    route_long_name VARCHAR(200),
    route_long_name_clean VARCHAR(200),
    route_type INTEGER,
    route_url VARCHAR(500),
    route_color VARCHAR(10),
    route_text_color VARCHAR(10),
    is_night_train BOOLEAN,
    train_category VARCHAR(10),
    operator_standardized VARCHAR(50),
    data_source VARCHAR(50),
    processed_date DATE,
    FOREIGN KEY (agency_id) REFERENCES operateurs(agency_id)
);

INDEX idx_lignes_agency ON lignes(agency_id);
INDEX idx_lignes_type ON lignes(route_type);

TABLE operateurs (
    agency_id VARCHAR(50) PRIMARY KEY,
    agency_name VARCHAR(200),
    agency_url VARCHAR(500),
    agency_timezone VARCHAR(50),
    agency_lang VARCHAR(10),
    agency_phone VARCHAR(50),
    agency_email VARCHAR(100)
);

INDEX idx_operateurs_timezone ON operateurs(agency_timezone);

TABLE trajets (
    trip_id VARCHAR(50) PRIMARY KEY,
    route_id VARCHAR(50),
    service_id VARCHAR(50),
    trip_headsign VARCHAR(200),
    direction_id INTEGER,
    block_id VARCHAR(50),
    shape_id VARCHAR(50),
    FOREIGN KEY (route_id) REFERENCES lignes(route_id)
);

INDEX idx_trajets_route ON trajets(route_id);
INDEX idx_trajets_service ON trajets(service_id);

TABLE horaires (
    horaire_id SERIAL PRIMARY KEY,
    trip_id VARCHAR(50),
    stop_id VARCHAR(50),
    arrival_time TIME,
    departure_time TIME,
    stop_sequence INTEGER,
    pickup_type INTEGER,
    drop_off_type INTEGER,
    is_night_time BOOLEAN,
    time_category VARCHAR(10),
    fuseau_horaire VARCHAR(10),
    processed_date DATE,
    FOREIGN KEY (stop_id) REFERENCES gares(stop_id),
    FOREIGN KEY (trip_id) REFERENCES trajets(trip_id)
);

INDEX idx_horaires_trip ON horaires(trip_id);
INDEX idx_horaires_stop ON horaires(stop_id);
INDEX idx_horaires_arrival ON horaires(arrival_time);
INDEX idx_horaires_night ON horaires(is_night_time);

TABLE trains_nuit_externes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200),
    operateur VARCHAR(100),
    ville_depart VARCHAR(100),
    ville_arrivee VARCHAR(100),
    distance_km INTEGER,
    duree_h DECIMAL(5, 2),
    gares_intermediaires TEXT,
    type_train VARCHAR(50),
    source VARCHAR(100),
    scraped_date DATE
);

INDEX idx_trainsnuit_operateur ON trains_nuit_externes(operateur);
INDEX idx_trainsnuit_source ON trains_nuit_externes(source);
