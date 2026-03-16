from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import time


# ═══════════════════════════════════════════════════════════
# OPERATEURS
# ═══════════════════════════════════════════════════════════

class OperateurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:        int
    nom:       str
    pays_code: str


# ═══════════════════════════════════════════════════════════
# GARES
# ═══════════════════════════════════════════════════════════

class GareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:        int
    nom:       str
    pays_code: str
    latitude:  Optional[float] = None
    longitude: Optional[float] = None


# ═══════════════════════════════════════════════════════════
# DESSERTES
# ═══════════════════════════════════════════════════════════

class DesserteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                str
    nom_ligne:         str
    type_ligne:        Optional[str] = None
    type_service:      str
    heure_depart:      Optional[time] = None
    heure_arrivee:     Optional[time] = None
    distance_km:       Optional[int] = None
    duree_h:           Optional[float] = None
    emissions_co2_gkm: Optional[float] = None
    frequence_hebdo:   Optional[int] = None
    traction:          Optional[str] = None
    source_donnee:     Optional[str] = None
    # FK résolues
    operateur_id:      Optional[int] = None
    gare_depart_id:    Optional[int] = None
    gare_arrivee_id:   Optional[int] = None


class DesserteDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                str
    nom_ligne:         str
    type_ligne:        Optional[str] = None
    type_service:      str
    heure_depart:      Optional[time] = None
    heure_arrivee:     Optional[time] = None
    distance_km:       Optional[int] = None
    duree_h:           Optional[float] = None
    emissions_co2_gkm: Optional[float] = None
    frequence_hebdo:   Optional[int] = None
    traction:          Optional[str] = None
    source_donnee:     Optional[str] = None
    operateur:         Optional[OperateurResponse] = None
    gare_depart:       Optional[GareResponse] = None
    gare_arrivee:      Optional[GareResponse] = None


# ═══════════════════════════════════════════════════════════
# COMPARAISONS (pour le dashboard)
# ═══════════════════════════════════════════════════════════

class StatsServiceResponse(BaseModel):
    type_service:      str
    total:             int
    co2_moyen:         Optional[float] = None
    duree_moyenne_h:   Optional[float] = None

class StatsPayResponse(BaseModel):
    pays_code:         str
    total_gares:       int
    total_dessertes:   int

class StatsOperateurResponse(BaseModel):
    operateur:         str
    pays_code:         str
    total_dessertes:   int
    nb_jour:           int
    nb_nuit:           int
