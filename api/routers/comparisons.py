from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.dependencies import get_db
from models.ligne_model import Ligne
from models.trajet_model import Trajet
from models.gare_model import Gare

router = APIRouter()

@router.get("/stats")
def get_global_stats(db: Session = Depends(get_db)):
    """
    Statistiques globales sur les données
    """
    total_lignes = db.query(func.count(Ligne.id_ligne)).scalar()
    total_trajets = db.query(func.count(Trajet.id_trajet)).scalar()
    total_gares = db.query(func.count(Gare.id_gare)).scalar()
    
    return {
        "total_lignes": total_lignes,
        "total_trajets": total_trajets,
        "total_gares": total_gares
    }


@router.get("/lignes-par-type")
def get_lignes_by_type(db: Session = Depends(get_db)):
    from models.ligne_train_model import LigneTrain
    
    stats = db.query(
        LigneTrain.type_transport,
        func.count(LigneTrain.id_ligne).label("count")
    ).group_by(LigneTrain.type_transport).all()
    
    return [
        {
            "type_transport": stat.type_transport,
            "nombre_lignes": stat.count
        }
        for stat in stats
    ]


@router.get("/top-operateurs")
def get_top_operateurs(limit: int = 10, db: Session = Depends(get_db)):
    """
    Top des opérateurs par nombre de lignes
    """
    from models.operateur_model import Operateur
    
    stats = db.query(
        Operateur.nom_operateur,
        func.count(Ligne.id_ligne).label("nombre_lignes")
    ).join(Ligne, Operateur.id_operateur == Ligne.id_operateur)\
     .group_by(Operateur.nom_operateur)\
     .order_by(func.count(Ligne.id_ligne).desc())\
     .limit(limit).all()
    
    return [
        {
            "operateur": stat.nom_operateur,
            "nombre_lignes": stat.nombre_lignes
        }
        for stat in stats
    ]


@router.get("/gares-les-plus-desservies")
def get_most_served_gares(limit: int = 10, db: Session = Depends(get_db)):
    """
    Gares les plus desservies (par nombre de passages)
    """
    from models.horaire_model import Horaire
    
    stats = db.query(
        Gare.nom_gare,
        func.count(Horaire.id_gare).label("nombre_passages")
    ).join(Horaire, Gare.id_gare == Horaire.id_gare)\
     .group_by(Gare.nom_gare)\
     .order_by(func.count(Horaire.id_gare).desc())\
     .limit(limit).all()
    
    return [
        {
            "gare": stat.nom_gare,
            "nombre_passages": stat.nombre_passages
        }
        for stat in stats
    ]


@router.get("/repartition-jour-nuit")
def get_repartition_jour_nuit(db: Session = Depends(get_db)):
    """
    Répartition des trajets jour/nuit basée sur l'heure de départ
    """
    from models.horaire_model import Horaire
    from sqlalchemy import case, func
    from datetime import time

    stats = db.query(
        case(
            (Horaire.heure_depart >= time(22, 0), "Nuit"),
            (Horaire.heure_depart <= time(6, 0), "Nuit"),
            else_="Jour"
        ).label("periode"),
        func.count(Horaire.id_trajet).label("nombre")
    ).group_by("periode").all()

    return [
        {"periode": stat.periode, "nombre": stat.nombre}
        for stat in stats
    ]


@router.get("/valeurs-manquantes")
def get_valeurs_manquantes(db: Session = Depends(get_db)):
    """
    Taux de valeurs manquantes par table
    """
    from models.horaire_model import Horaire
    from models.operateur_model import Operateur

    # Gares
    total_gares = db.query(func.count(Gare.id_gare)).scalar()
    gares_sans_lat = db.query(func.count(Gare.id_gare)).filter(Gare.latitude == None).scalar()
    gares_sans_lon = db.query(func.count(Gare.id_gare)).filter(Gare.longitude == None).scalar()

    # Lignes
    total_lignes = db.query(func.count(Ligne.id_ligne)).scalar()
    lignes_sans_nom = db.query(func.count(Ligne.id_ligne)).filter(Ligne.nom_complet_ligne == None).scalar()
    lignes_sans_couleur = db.query(func.count(Ligne.id_ligne)).filter(Ligne.couleur_ligne == None).scalar()

    # Trajets
    total_trajets = db.query(func.count(Trajet.id_trajet)).scalar()
    trajets_sans_destination = db.query(func.count(Trajet.id_trajet)).filter(Trajet.destination_affichee == None).scalar()

    # Horaires
    total_horaires = db.query(func.count(Horaire.id_trajet)).scalar()
    horaires_sans_arrivee = db.query(func.count(Horaire.id_trajet)).filter(Horaire.heure_arrivee == None).scalar()
    horaires_sans_depart = db.query(func.count(Horaire.id_trajet)).filter(Horaire.heure_depart == None).scalar()

    def taux(manquants, total):
        return round((manquants / total * 100), 2) if total > 0 else 0

    return [
        {"champ": "Gares - Latitude", "taux_manquant": taux(gares_sans_lat, total_gares)},
        {"champ": "Gares - Longitude", "taux_manquant": taux(gares_sans_lon, total_gares)},
        {"champ": "Lignes - Nom complet", "taux_manquant": taux(lignes_sans_nom, total_lignes)},
        {"champ": "Lignes - Couleur", "taux_manquant": taux(lignes_sans_couleur, total_lignes)},
        {"champ": "Trajets - Destination", "taux_manquant": taux(trajets_sans_destination, total_trajets)},
        {"champ": "Horaires - Heure arrivée", "taux_manquant": taux(horaires_sans_arrivee, total_horaires)},
        {"champ": "Horaires - Heure départ", "taux_manquant": taux(horaires_sans_depart, total_horaires)},
    ]