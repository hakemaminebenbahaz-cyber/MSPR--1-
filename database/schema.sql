-- ============================================================
-- ObRail Europe — Schéma PostgreSQL
-- À exécuter sur Azure Database for PostgreSQL
-- ============================================================

-- ─────────────────────────────────────────────
-- Table : operateurs
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS operateurs (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    pays_code   CHAR(2)      NOT NULL
);

-- ─────────────────────────────────────────────
-- Table : gares
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gares (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(150) NOT NULL,
    ville       VARCHAR(100),
    pays_code   CHAR(2)      NOT NULL,
    latitude    DOUBLE PRECISION,
    longitude   DOUBLE PRECISION
);

-- ─────────────────────────────────────────────
-- Table : dessertes  (table principale)
-- Représente une liaison ferroviaire entre deux gares
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dessertes (
    id                  VARCHAR(20)  PRIMARY KEY,   -- ex: AT_NJ_VIE
    operateur_id        INTEGER      REFERENCES operateurs(id) ON DELETE SET NULL,
    nom_ligne           VARCHAR(200) NOT NULL,
    type_ligne          VARCHAR(50),                -- Intercité, Grande vitesse, Train de nuit intern, Régional
    type_service        VARCHAR(10)  NOT NULL        -- Jour / Nuit
                        CHECK (type_service IN ('Jour', 'Nuit')),
    gare_depart_id      INTEGER      REFERENCES gares(id) ON DELETE SET NULL,
    gare_arrivee_id     INTEGER      REFERENCES gares(id) ON DELETE SET NULL,
    heure_depart        TIME,
    heure_arrivee       TIME,
    distance_km         INTEGER,
    duree_h             NUMERIC(5, 2),
    emissions_co2_gkm   NUMERIC(6, 2),             -- gCO2 par km-passager
    frequence_hebdo     INTEGER,                    -- nombre de trajets par semaine
    traction            VARCHAR(20),                -- électrique / diesel / mixte
    source_donnee       VARCHAR(100)
);

-- ─────────────────────────────────────────────
-- Index utiles pour l'API
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_dessertes_type_service   ON dessertes(type_service);
CREATE INDEX IF NOT EXISTS idx_dessertes_gare_depart    ON dessertes(gare_depart_id);
CREATE INDEX IF NOT EXISTS idx_dessertes_gare_arrivee   ON dessertes(gare_arrivee_id);
CREATE INDEX IF NOT EXISTS idx_gares_pays               ON gares(pays_code);
CREATE INDEX IF NOT EXISTS idx_gares_nom                ON gares(nom);
