from sqlalchemy import Column, Integer, String, Numeric, Time, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from core.database import Base


class Operateur(Base):
    __tablename__ = "operateurs"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    nom      = Column(String(100), nullable=False)
    pays_code = Column(CHAR(2), nullable=False)

    dessertes = relationship("Desserte", back_populates="operateur")


class Gare(Base):
    __tablename__ = "gares"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    nom       = Column(String(150), nullable=False)
    pays_code = Column(CHAR(2), nullable=False)
    latitude  = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    dessertes_depart  = relationship("Desserte", foreign_keys="Desserte.gare_depart_id",  back_populates="gare_depart")
    dessertes_arrivee = relationship("Desserte", foreign_keys="Desserte.gare_arrivee_id", back_populates="gare_arrivee")


class Desserte(Base):
    __tablename__ = "dessertes"

    id               = Column(String(20),  primary_key=True)
    operateur_id     = Column(Integer, ForeignKey("operateurs.id"))
    nom_ligne        = Column(String(200), nullable=False)
    type_ligne       = Column(String(50))
    type_service     = Column(String(10),  nullable=False)
    gare_depart_id   = Column(Integer, ForeignKey("gares.id"))
    gare_arrivee_id  = Column(Integer, ForeignKey("gares.id"))
    heure_depart     = Column(Time)
    heure_arrivee    = Column(Time)
    distance_km      = Column(Integer)
    duree_h          = Column(Numeric(5, 2))
    emissions_co2_gkm = Column(Numeric(6, 2))
    frequence_hebdo  = Column(Integer)
    traction         = Column(String(20))
    source_donnee    = Column(String(100))

    operateur    = relationship("Operateur", back_populates="dessertes")
    gare_depart  = relationship("Gare", foreign_keys=[gare_depart_id],  back_populates="dessertes_depart")
    gare_arrivee = relationship("Gare", foreign_keys=[gare_arrivee_id], back_populates="dessertes_arrivee")
