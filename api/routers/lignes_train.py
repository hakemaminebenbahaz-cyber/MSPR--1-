from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from models.ligne_train_model import LigneTrain
from schemas.responses import LigneResponse

router = APIRouter()

@router.get("/", response_model=List[LigneResponse])
def get_all_lignes_train(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère uniquement les lignes de train (sans bus)
    """
    lignes = db.query(LigneTrain).offset(skip).limit(limit).all()
    return lignes


@router.get("/{id_ligne}", response_model=LigneResponse)
def get_ligne_train(id_ligne: str, db: Session = Depends(get_db)):
    """
    Récupère une ligne de train par son ID
    """
    ligne = db.query(LigneTrain).filter(LigneTrain.id_ligne == id_ligne).first()
    if not ligne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ligne de train avec l'ID '{id_ligne}' non trouvée"
        )
    return ligne


@router.get("/search/nom", response_model=List[LigneResponse])
def search_lignes_train_by_nom(
    nom: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """
    Recherche des lignes de train par nom
    """
    lignes = db.query(LigneTrain).filter(
        LigneTrain.nom_complet_ligne.ilike(f"%{nom}%")
    ).all()
    return lignes


@router.get("/search/code", response_model=List[LigneResponse])
def search_lignes_train_by_code(
    code: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    Recherche des lignes de train par code
    """
    lignes = db.query(LigneTrain).filter(
        LigneTrain.code_ligne.ilike(f"%{code}%")
    ).all()
    return lignes