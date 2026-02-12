from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db
from core.exceptions import GareNotFoundException
from models.gare_model import Gare
from schemas.responses import GareResponse
from schemas.requests import GareCreate, GareUpdate

router = APIRouter()

# ========== GET ALL GARES ==========
@router.get("/", response_model=List[GareResponse])
def get_all_gares(
    skip: int = Query(0, ge=0, description="Nombre de résultats à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre de résultats à retourner"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de toutes les gares avec pagination
    """
    gares = db.query(Gare).offset(skip).limit(limit).all()
    return gares


# ========== GET ONE GARE ==========
@router.get("/{id_gare}", response_model=GareResponse)
def get_gare(id_gare: str, db: Session = Depends(get_db)):
    """
    Récupère une gare par son ID
    """
    gare = db.query(Gare).filter(Gare.id_gare == id_gare).first()
    if not gare:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gare avec l'ID '{id_gare}' non trouvée"
        )
    return gare


# ========== SEARCH GARES BY NAME ==========
@router.get("/search/nom", response_model=List[GareResponse])
def search_gares_by_name(
    nom: str = Query(..., min_length=2, description="Nom de la gare à rechercher"),
    db: Session = Depends(get_db)
):
    """
    Recherche des gares par nom (recherche partielle)
    """
    gares = db.query(Gare).filter(
        Gare.nom_gare.ilike(f"%{nom}%")
    ).all()
    return gares


# ========== CREATE GARE ==========
@router.post("/", response_model=GareResponse, status_code=status.HTTP_201_CREATED)
def create_gare(gare: GareCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle gare
    """
    # Vérifier si la gare existe déjà
    existing = db.query(Gare).filter(Gare.id_gare == gare.id_gare).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Une gare avec l'ID '{gare.id_gare}' existe déjà"
        )
    
    new_gare = Gare(**gare.model_dump())
    db.add(new_gare)
    db.commit()
    db.refresh(new_gare)
    return new_gare


# ========== UPDATE GARE ==========
@router.put("/{id_gare}", response_model=GareResponse)
def update_gare(id_gare: str, gare_update: GareUpdate, db: Session = Depends(get_db)):
    """
    Met à jour une gare existante
    """
    gare = db.query(Gare).filter(Gare.id_gare == id_gare).first()
    if not gare:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gare avec l'ID '{id_gare}' non trouvée"
        )
    
    # Mettre à jour les champs fournis
    update_data = gare_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(gare, key, value)
    
    db.commit()
    db.refresh(gare)
    return gare


# ========== DELETE GARE ==========
@router.delete("/{id_gare}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gare(id_gare: str, db: Session = Depends(get_db)):
    """
    Supprime une gare
    """
    gare = db.query(Gare).filter(Gare.id_gare == id_gare).first()
    if not gare:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gare avec l'ID '{id_gare}' non trouvée"
        )
    
    db.delete(gare)
    db.commit()
    return None