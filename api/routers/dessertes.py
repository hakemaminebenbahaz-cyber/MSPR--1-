from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from core.dependencies import get_db
from models.models import Desserte, Gare, Operateur
from schemas.responses import DesserteResponse, DesserteDetailResponse

router = APIRouter()


@router.get("/", response_model=List[DesserteDetailResponse])
def get_dessertes(
    depart: Optional[str] = Query(None, description="Nom partiel de la gare de départ"),
    arrivee: Optional[str] = Query(None, description="Nom partiel de la gare d'arrivée"),
    type_service: Optional[str] = Query(None, description="Jour ou Nuit"),
    type_ligne: Optional[str] = Query(None, description="Grande vitesse, Intercité, Train régional, Train de nuit intern"),
    operateur: Optional[str] = Query(None, description="Nom partiel de l'opérateur"),
    pays_code: Optional[str] = Query(None, description="Pays de la gare de départ (FR, DE, ...)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Recherche de dessertes ferroviaires avec filtres.
    - **depart** : nom partiel de la gare de départ
    - **arrivee** : nom partiel de la gare d'arrivée
    - **type_service** : Jour ou Nuit
    - **type_ligne** : Grande vitesse, Intercité, Train régional
    - **operateur** : nom partiel de l'opérateur
    - **pays_code** : pays de la gare de départ
    """
    GareDepart  = Gare.__table__.alias("gare_dep")
    GareArrivee = Gare.__table__.alias("gare_arr")

    query = (
        db.query(Desserte)
        .options(
            joinedload(Desserte.operateur),
            joinedload(Desserte.gare_depart),
            joinedload(Desserte.gare_arrivee),
        )
    )

    if depart:
        query = query.join(Desserte.gare_depart).filter(Gare.nom.ilike(f"%{depart}%"))
    if arrivee:
        query = query.join(Desserte.gare_arrivee).filter(Gare.nom.ilike(f"%{arrivee}%"))
    if type_service:
        query = query.filter(Desserte.type_service == type_service)
    if type_ligne:
        query = query.filter(Desserte.type_ligne.ilike(f"%{type_ligne}%"))
    if operateur:
        query = query.join(Desserte.operateur).filter(Operateur.nom.ilike(f"%{operateur}%"))
    if pays_code:
        if depart is None:
            query = query.join(Desserte.gare_depart)
        query = query.filter(Gare.pays_code == pays_code.upper())

    return query.offset(skip).limit(limit).all()


@router.get("/{desserte_id}", response_model=DesserteDetailResponse)
def get_desserte(desserte_id: str, db: Session = Depends(get_db)):
    """Récupère une desserte par son ID avec tous les détails."""
    d = (
        db.query(Desserte)
        .options(
            joinedload(Desserte.operateur),
            joinedload(Desserte.gare_depart),
            joinedload(Desserte.gare_arrivee),
        )
        .filter(Desserte.id == desserte_id)
        .first()
    )
    if not d:
        raise HTTPException(status_code=404, detail=f"Desserte '{desserte_id}' introuvable")
    return d
