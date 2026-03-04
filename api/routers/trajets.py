from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, aliased
from typing import List, Optional

from core.dependencies import get_db
from models.trajet_model import Trajet
from models.horaire_model import Horaire
from models.ligne_model import Ligne
from models.gare_model import Gare
from models.operateur_model import Operateur
from schemas.responses import TrajetResponse, TrajetDetailResponse, RechercheDesserteResponse

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


@router.get("/recherche", response_model=List[RechercheDesserteResponse])
def recherche_dessertes(
    depart: Optional[str] = Query(None, description="Nom de la ville ou gare de départ"),
    arrivee: Optional[str] = Query(None, description="Nom de la ville ou gare d'arrivée"),
    type_transport: Optional[int] = Query(None, description="Type de transport GTFS (2=Train, 0=Tram, 1=Métro...)"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Recherche des dessertes ferroviaires selon différents critères.
    - **depart** : nom partiel de la gare de départ
    - **arrivee** : nom partiel de la gare d'arrivée
    - **type_transport** : type GTFS (2 = Train, 0 = Tram, 1 = Métro, 3 = Bus)
    """
    GareDepart = aliased(Gare)
    GareArrivee = aliased(Gare)

    query = (
        db.query(
            Horaire.id_trajet,
            Horaire.gare_depart,
            Horaire.gare_arrivee,
            GareDepart.nom_gare.label("nom_gare_depart"),
            GareArrivee.nom_gare.label("nom_gare_arrivee"),
            Horaire.heure_depart,
            Horaire.heure_arrivee,
            Trajet.destination_affichee,
            Ligne.type_transport,
            Ligne.nom_complet_ligne.label("nom_ligne"),
            Operateur.nom_operateur.label("operateur"),
        )
        .join(Trajet, Horaire.id_trajet == Trajet.id_trajet)
        .join(Ligne, Trajet.id_ligne == Ligne.id_ligne)
        .join(Operateur, Ligne.id_operateur == Operateur.id_operateur)
        .outerjoin(GareDepart, Horaire.gare_depart == GareDepart.id_gare)
        .outerjoin(GareArrivee, Horaire.gare_arrivee == GareArrivee.id_gare)
    )

    if depart:
        query = query.filter(GareDepart.nom_gare.ilike(f"%{depart}%"))
    if arrivee:
        query = query.filter(GareArrivee.nom_gare.ilike(f"%{arrivee}%"))
    if type_transport is not None:
        query = query.filter(Ligne.type_transport == type_transport)

    results = query.limit(limit).all()

    return [
        RechercheDesserteResponse(
            id_trajet=r.id_trajet,
            gare_depart=r.gare_depart,
            gare_arrivee=r.gare_arrivee,
            nom_gare_depart=r.nom_gare_depart,
            nom_gare_arrivee=r.nom_gare_arrivee,
            heure_depart=r.heure_depart,
            heure_arrivee=r.heure_arrivee,
            destination_affichee=r.destination_affichee,
            type_transport=r.type_transport,
            nom_ligne=r.nom_ligne,
            operateur=r.operateur,
        )
        for r in results
    ]


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