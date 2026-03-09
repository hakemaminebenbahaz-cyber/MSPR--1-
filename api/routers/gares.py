from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db
from models.models import Gare
from schemas.responses import GareResponse

router = APIRouter()


@router.get("/", response_model=List[GareResponse])
def get_gares(
    pays_code: Optional[str] = Query(None, description="Filtrer par pays (FR, DE, ...)"),
    nom: Optional[str] = Query(None, description="Recherche partielle par nom"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Liste les gares avec filtres optionnels."""
    query = db.query(Gare)
    if pays_code:
        query = query.filter(Gare.pays_code == pays_code.upper())
    if nom:
        query = query.filter(Gare.nom.ilike(f"%{nom}%"))
    return query.order_by(Gare.nom).offset(skip).limit(limit).all()


@router.get("/map/coords", response_model=List[GareResponse])
def get_gares_map(db: Session = Depends(get_db)):
    """Toutes les gares avec coordonnées GPS (pour la carte)."""
    return db.query(Gare).filter(
        Gare.latitude.isnot(None),
        Gare.longitude.isnot(None)
    ).all()


@router.get("/{gare_id}", response_model=GareResponse)
def get_gare(gare_id: int, db: Session = Depends(get_db)):
    """Récupère une gare par son ID."""
    gare = db.query(Gare).filter(Gare.id == gare_id).first()
    if not gare:
        raise HTTPException(status_code=404, detail=f"Gare {gare_id} introuvable")
    return gare
