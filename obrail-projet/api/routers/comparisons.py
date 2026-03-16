from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased
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


@router.get("/qualite-donnees")
def get_qualite_donnees(db: Session = Depends(get_db)):
    """Taux de complétude des champs clés pour les 3 tables."""

    def completude(model, col, total):
        nulls = db.query(func.count(model.id)).filter(col.is_(None)).scalar()
        complet = total - nulls
        return complet, nulls, round(complet / total * 100, 1) if total else 0

    result = []

    # ── Opérateurs
    total_op = db.query(func.count(Operateur.id)).scalar()
    for key, label, col in [
        ("nom",       "Nom",       Operateur.nom),
        ("pays_code", "Pays code", Operateur.pays_code),
    ]:
        remplis, manquants, taux = completude(Operateur, col, total_op)
        result.append({"table": "operateurs", "champ": key, "label": label,
                        "total": total_op, "remplis": remplis, "manquants": manquants, "taux_completude": taux})

    # ── Gares
    total_g = db.query(func.count(Gare.id)).scalar()
    for key, label, col in [
        ("nom",       "Nom",       Gare.nom),
        ("pays_code", "Pays code", Gare.pays_code),
        ("latitude",  "Latitude",  Gare.latitude),
        ("longitude", "Longitude", Gare.longitude),
    ]:
        remplis, manquants, taux = completude(Gare, col, total_g)
        result.append({"table": "gares", "champ": key, "label": label,
                        "total": total_g, "remplis": remplis, "manquants": manquants, "taux_completude": taux})

    # ── Dessertes
    total_d = db.query(func.count(Desserte.id)).scalar()
    for key, label, col in [
        ("operateur_id",      "Opérateur",      Desserte.operateur_id),
        ("nom_ligne",         "Nom de ligne",   Desserte.nom_ligne),
        ("type_ligne",        "Type de ligne",  Desserte.type_ligne),
        ("type_service",      "Type de service",Desserte.type_service),
        ("gare_depart_id",    "Gare de départ", Desserte.gare_depart_id),
        ("gare_arrivee_id",   "Gare d'arrivée", Desserte.gare_arrivee_id),
        ("distance_km",       "Distance (km)",  Desserte.distance_km),
        ("duree_h",           "Durée (h)",      Desserte.duree_h),
        ("frequence_hebdo",   "Fréquence hebdo",Desserte.frequence_hebdo),
        ("emissions_co2_gkm", "Émissions CO₂",  Desserte.emissions_co2_gkm),
        ("traction",          "Traction",       Desserte.traction),
        ("heure_depart",      "Heure départ",   Desserte.heure_depart),
        ("heure_arrivee",     "Heure arrivée",  Desserte.heure_arrivee),
    ]:
        remplis, manquants, taux = completude(Desserte, col, total_d)
        result.append({"table": "dessertes", "champ": key, "label": label,
                        "total": total_d, "remplis": remplis, "manquants": manquants, "taux_completude": taux})

    return result


@router.get("/inter-pays")
def get_inter_pays(db: Session = Depends(get_db)):
    """Trajets internationaux (départ et arrivée dans des pays différents)."""
    GareDep = aliased(Gare, name="gare_dep")
    GareArr = aliased(Gare, name="gare_arr")

    rows = (
        db.query(
            GareDep.pays_code.label("pays_depart"),
            GareArr.pays_code.label("pays_arrivee"),
            Desserte.nom_ligne,
            Desserte.type_service,
            GareDep.nom.label("gare_depart"),
            GareArr.nom.label("gare_arrivee"),
            Desserte.heure_depart,
            Desserte.heure_arrivee,
            Desserte.duree_h,
        )
        .join(GareDep, Desserte.gare_depart_id == GareDep.id)
        .join(GareArr, Desserte.gare_arrivee_id == GareArr.id)
        .filter(GareDep.pays_code != GareArr.pays_code)
        .order_by(GareDep.pays_code, GareArr.pays_code)
        .all()
    )

    return [
        {
            "pays_depart":  r.pays_depart,
            "pays_arrivee": r.pays_arrivee,
            "liaison":      f"{r.pays_depart} → {r.pays_arrivee}",
            "nom_ligne":    r.nom_ligne,
            "type_service": r.type_service,
            "gare_depart":  r.gare_depart,
            "gare_arrivee": r.gare_arrivee,
            "heure_depart": str(r.heure_depart) if r.heure_depart else None,
            "heure_arrivee": str(r.heure_arrivee) if r.heure_arrivee else None,
            "duree_h":      float(r.duree_h) if r.duree_h else None,
        }
        for r in rows
    ]
