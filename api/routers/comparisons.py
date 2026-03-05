from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.dependencies import get_db
from models.models import Desserte, Gare, Operateur
from schemas.responses import StatsServiceResponse, StatsPayResponse, StatsOperateurResponse

router = APIRouter()


@router.get("/stats-globales")
def get_stats_globales(db: Session = Depends(get_db)):
    """Statistiques globales : totaux par table."""
    return {
        "total_operateurs": db.query(func.count(Operateur.id)).scalar(),
        "total_gares":      db.query(func.count(Gare.id)).scalar(),
        "total_dessertes":  db.query(func.count(Desserte.id)).scalar(),
        "total_jour":       db.query(func.count(Desserte.id)).filter(Desserte.type_service == "Jour").scalar(),
        "total_nuit":       db.query(func.count(Desserte.id)).filter(Desserte.type_service == "Nuit").scalar(),
    }


@router.get("/jour-vs-nuit", response_model=list[StatsServiceResponse])
def get_jour_vs_nuit(db: Session = Depends(get_db)):
    """Comparaison Jour vs Nuit : nombre, CO2 moyen, durée moyenne."""
    stats = (
        db.query(
            Desserte.type_service,
            func.count(Desserte.id).label("total"),
            func.avg(Desserte.emissions_co2_gkm).label("co2_moyen"),
            func.avg(Desserte.duree_h).label("duree_moyenne_h"),
        )
        .group_by(Desserte.type_service)
        .all()
    )
    return [
        StatsServiceResponse(
            type_service=r.type_service,
            total=r.total,
            co2_moyen=round(float(r.co2_moyen), 2) if r.co2_moyen else None,
            duree_moyenne_h=round(float(r.duree_moyenne_h), 2) if r.duree_moyenne_h else None,
        )
        for r in stats
    ]


@router.get("/par-type-ligne")
def get_par_type_ligne(db: Session = Depends(get_db)):
    """Répartition des dessertes par type de ligne."""
    stats = (
        db.query(
            Desserte.type_ligne,
            func.count(Desserte.id).label("total"),
            func.avg(Desserte.emissions_co2_gkm).label("co2_moyen"),
        )
        .group_by(Desserte.type_ligne)
        .all()
    )
    return [
        {
            "type_ligne": r.type_ligne,
            "total": r.total,
            "co2_moyen": round(float(r.co2_moyen), 2) if r.co2_moyen else None,
        }
        for r in stats
    ]


@router.get("/par-pays", response_model=list[StatsPayResponse])
def get_par_pays(db: Session = Depends(get_db)):
    """Nombre de gares et dessertes par pays."""
    gares_stats = (
        db.query(Gare.pays_code, func.count(Gare.id).label("total_gares"))
        .group_by(Gare.pays_code)
        .all()
    )
    dessertes_stats = (
        db.query(Gare.pays_code, func.count(Desserte.id).label("total_dessertes"))
        .join(Desserte, Gare.id == Desserte.gare_depart_id)
        .group_by(Gare.pays_code)
        .all()
    )
    dest_map = {r.pays_code: r.total_dessertes for r in dessertes_stats}
    return [
        StatsPayResponse(
            pays_code=r.pays_code,
            total_gares=r.total_gares,
            total_dessertes=dest_map.get(r.pays_code, 0),
        )
        for r in gares_stats
    ]


@router.get("/par-operateur", response_model=list[StatsOperateurResponse])
def get_par_operateur(db: Session = Depends(get_db)):
    """Nombre de dessertes Jour/Nuit par opérateur."""
    stats = (
        db.query(
            Operateur.nom,
            Operateur.pays_code,
            func.count(Desserte.id).label("total"),
            func.sum(
                func.cast(Desserte.type_service == "Jour", func.Integer if False else Desserte.id.__class__)
            ).label("nb_jour"),
        )
        .join(Desserte, Operateur.id == Desserte.operateur_id)
        .group_by(Operateur.nom, Operateur.pays_code)
        .all()
    )

    # Calcul nb_jour et nb_nuit séparément pour éviter les casts complexes
    result = []
    for op in db.query(Operateur).all():
        total = db.query(func.count(Desserte.id)).filter(Desserte.operateur_id == op.id).scalar()
        if total == 0:
            continue
        nb_jour = db.query(func.count(Desserte.id)).filter(
            Desserte.operateur_id == op.id, Desserte.type_service == "Jour"
        ).scalar()
        result.append(StatsOperateurResponse(
            operateur=op.nom,
            pays_code=op.pays_code,
            total_dessertes=total,
            nb_jour=nb_jour,
            nb_nuit=total - nb_jour,
        ))
    return sorted(result, key=lambda x: x.total_dessertes, reverse=True)
