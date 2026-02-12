from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from models.ligne_model import Ligne
from schemas.responses import LigneResponse
from schemas.requests import LigneCreate, LigneUpdate

router = APIRouter()

@router.get("/", response_model=List[LigneResponse])
def get_all_lignes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de toutes les lignes
    """
    lignes = db.query(Ligne).offset(skip).limit(limit).all()
    return lignes


@router.get("/{id_ligne}", response_model=LigneResponse)
def get_ligne(id_ligne: str, db: Session = Depends(get_db)):
    """
    Récupère une ligne par son ID
    """
    ligne = db.query(Ligne).filter(Ligne.id_ligne == id_ligne).first()
    if not ligne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ligne avec l'ID '{id_ligne}' non trouvée"
        )
    return ligne


@router.get("/search/code", response_model=List[LigneResponse])
def search_lignes_by_code(
    code: str = Query(..., description="Code de la ligne"),
    db: Session = Depends(get_db)
):
    """
    Recherche des lignes par code
    """
    lignes = db.query(Ligne).filter(Ligne.code_ligne.ilike(f"%{code}%")).all()
    return lignes