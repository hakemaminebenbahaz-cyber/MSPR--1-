from pydantic import BaseModel, Field
from typing import Optional

# ========== GARES ==========
class GareCreate(BaseModel):
    id_gare: str = Field(..., max_length=100)
    nom_gare: str = Field(..., min_length=1, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    gare_parente: Optional[str] = Field(None, max_length=100)

class GareUpdate(BaseModel):
    nom_gare: Optional[str] = Field(None, min_length=1, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

# ========== LIGNES ==========
class LigneCreate(BaseModel):
    id_ligne: str = Field(..., max_length=100)
    id_operateur: str = Field(..., max_length=100)
    code_ligne: str = Field(..., min_length=1, max_length=20)
    nom_complet_ligne: Optional[str] = None
    type_transport: Optional[int] = None
    couleur_ligne: Optional[str] = Field(None, max_length=6)

class LigneUpdate(BaseModel):
    code_ligne: Optional[str] = Field(None, min_length=1, max_length=20)
    nom_complet_ligne: Optional[str] = None
    type_transport: Optional[int] = None
    couleur_ligne: Optional[str] = Field(None, max_length=6)

# ========== OPERATEURS ==========
class OperateurCreate(BaseModel):
    id_operateur: str = Field(..., max_length=100)
    nom_operateur: str = Field(..., min_length=1, max_length=200)
    site_web: Optional[str] = Field(None, max_length=500)
    fuseau_horaire: Optional[str] = Field(None, max_length=50)
    langue: Optional[str] = Field(None, max_length=2)