from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db
from models.operateur_model import Operateur
from schemas.responses import OperateurResponse
from schemas.requests import OperateurCreate

router = APIRouter()

@router.get("/", response_model=List[OperateurResponse])
def get_all_operateurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de tous les opérateurs
    """
    operateurs = db.query(Operateur).offset(skip).limit(limit).all()
    return operateurs


@router.get("/{id_operateur}", response_model=OperateurResponse)
def get_operateur(id_operateur: str, db: Session = Depends(get_db)):
    """
    Récupère un opérateur par son ID
    """
    operateur = db.query(Operateur).filter(Operateur.id_operateur == id_operateur).first()
    if not operateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opérateur avec l'ID '{id_operateur}' non trouvé"
        )
    return operateur


@router.get("/search/nom", response_model=List[OperateurResponse])
def search_operateurs_by_name(
    nom: str = Query(..., min_length=2, description="Nom de l'opérateur"),
    db: Session = Depends(get_db)
):
    """
    Recherche des opérateurs par nom
    """
    operateurs = db.query(Operateur).filter(
        Operateur.nom_operateur.ilike(f"%{nom}%")
    ).all()
    return operateurs


@router.post("/", response_model=OperateurResponse, status_code=status.HTTP_201_CREATED)
def create_operateur(operateur: OperateurCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel opérateur
    """
    existing = db.query(Operateur).filter(Operateur.id_operateur == operateur.id_operateur).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un opérateur avec l'ID '{operateur.id_operateur}' existe déjà"
        )
    
    new_operateur = Operateur(**operateur.model_dump())
    db.add(new_operateur)
    db.commit()
    db.refresh(new_operateur)
    return new_operateur