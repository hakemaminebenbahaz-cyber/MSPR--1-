from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import time

# ========== OPERATEURS ==========
class OperateurResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_operateur: str
    nom_operateur: str
    site_web: Optional[str] = None
    fuseau_horaire: Optional[str] = None
    langue: Optional[str] = None

# ========== GARES ==========
class GareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_gare: str
    nom_gare: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gare_parente: Optional[str] = None

# ========== LIGNES ==========
class LigneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_ligne: str
    id_operateur: str
    code_ligne: str
    nom_complet_ligne: Optional[str] = None
    type_transport: Optional[int] = None
    couleur_ligne: Optional[str] = None

# ========== CALENDRIER ==========
class CalendrierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_service: int
    date_circulation: int
    type_exception: Optional[int] = None

# ========== TRAJETS ==========
class TrajetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_trajet: str
    id_ligne: str
    id_service: Optional[int] = None
    date_circulation: Optional[int] = None
    destination_affichee: Optional[str] = None
    sens_circulation: Optional[int] = None

# ========== HORAIRES ==========
class HoraireResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_trajet: str
    heure_arrivee: Optional[time] = None
    heure_depart: Optional[time] = None
    id_gare: str
    ordre_arret: int

# ========== RÉPONSES ENRICHIES ==========
class LigneDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_ligne: str
    code_ligne: str
    nom_complet_ligne: Optional[str] = None
    operateur: OperateurResponse

class TrajetDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id_trajet: str
    destination_affichee: Optional[str] = None
    ligne: LigneResponse
    horaires: list[HoraireResponse] = []