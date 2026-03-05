from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db
from models.models import Operateur
from schemas.responses import OperateurResponse

router = APIRouter()


@router.get("/", response_model=List[OperateurResponse])
def get_operateurs(
    pays_code: Optional[str] = Query(None, description="Filtrer par pays (FR, DE, ...)"),
    db: Session = Depends(get_db)
):
    """Liste tous les opérateurs ferroviaires."""
    query = db.query(Operateur)
    if pays_code:
        query = query.filter(Operateur.pays_code == pays_code.upper())
    return query.order_by(Operateur.nom).all()


@router.get("/{operateur_id}", response_model=OperateurResponse)
def get_operateur(operateur_id: int, db: Session = Depends(get_db)):
    """Récupère un opérateur par son ID."""
    op = db.query(Operateur).filter(Operateur.id == operateur_id).first()
    if not op:
        raise HTTPException(status_code=404, detail=f"Opérateur {operateur_id} introuvable")
    return op
