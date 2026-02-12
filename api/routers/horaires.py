from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from models.horaire_model import Horaire
from schemas.responses import HoraireResponse

router = APIRouter()

@router.get("/", response_model=List[HoraireResponse])
def get_all_horaires(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les horaires
    """
    horaires = db.query(Horaire).offset(skip).limit(limit).all()
    return horaires


@router.get("/trajet/{id_trajet}", response_model=List[HoraireResponse])
def get_horaires_by_trajet(
    id_trajet: str,
    db: Session = Depends(get_db)
):
    """
    Récupère tous les horaires d'un trajet spécifique (ordonnés par ordre d'arrêt)
    """
    horaires = db.query(Horaire).filter(
        Horaire.id_trajet == id_trajet
    ).order_by(Horaire.ordre_arret).all()
    
    if not horaires:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun horaire trouvé pour le trajet '{id_trajet}'"
        )
    return horaires


@router.get("/gare/{id_gare}", response_model=List[HoraireResponse])
def get_horaires_by_gare(
    id_gare: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les horaires d'une gare spécifique
    """
    horaires = db.query(Horaire).filter(
        Horaire.id_gare == id_gare
    ).offset(skip).limit(limit).all()
    
    if not horaires:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun horaire trouvé pour la gare '{id_gare}'"
        )
    return horaires