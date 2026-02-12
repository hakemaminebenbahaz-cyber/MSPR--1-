from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db
from models.trajet_model import Trajet
from models.horaire_model import Horaire
from schemas.responses import TrajetResponse, TrajetDetailResponse

router = APIRouter()

@router.get("/", response_model=List[TrajetResponse])
def get_all_trajets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    destination: Optional[str] = Query(None, description="Filtrer par destination"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les trajets avec filtres optionnels
    """
    query = db.query(Trajet)
    
    if destination:
        query = query.filter(Trajet.destination_affichee.ilike(f"%{destination}%"))
    
    trajets = query.offset(skip).limit(limit).all()
    return trajets


@router.get("/{id_trajet}", response_model=TrajetResponse)
def get_trajet(id_trajet: str, db: Session = Depends(get_db)):
    """
    Récupère un trajet par son ID
    """
    trajet = db.query(Trajet).filter(Trajet.id_trajet == id_trajet).first()
    if not trajet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trajet avec l'ID '{id_trajet}' non trouvé"
        )
    return trajet


@router.get("/{id_trajet}/detail", response_model=TrajetDetailResponse)
def get_trajet_detail(id_trajet: str, db: Session = Depends(get_db)):
    """
    Récupère un trajet avec tous ses horaires
    """
    trajet = db.query(Trajet).filter(Trajet.id_trajet == id_trajet).first()
    if not trajet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trajet avec l'ID '{id_trajet}' non trouvé"
        )
    
    # Récupérer les horaires du trajet
    horaires = db.query(Horaire).filter(
        Horaire.id_trajet == id_trajet
    ).order_by(Horaire.ordre_arret).all()
    
    return {
        "id_trajet": trajet.id_trajet,
        "destination_affichee": trajet.destination_affichee,
        "ligne": trajet.ligne,
        "horaires": horaires
    }


@router.get("/ligne/{id_ligne}", response_model=List[TrajetResponse])
def get_trajets_by_ligne(
    id_ligne: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les trajets d'une ligne spécifique
    """
    trajets = db.query(Trajet).filter(
        Trajet.id_ligne == id_ligne
    ).offset(skip).limit(limit).all()
    return trajets