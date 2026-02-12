from sqlalchemy import Column, String, Time, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Horaire(Base):
    __tablename__ = "horaires"
    
    id_trajet = Column(String(100), ForeignKey("trajets.id_trajet"), primary_key=True)
    heure_arrivee = Column(Time)
    heure_depart = Column(Time)
    id_gare = Column(String(100), ForeignKey("gares.id_gare"), primary_key=True)
    ordre_arret = Column(Integer, nullable=False, primary_key=True)
    
    # Relations
    trajet = relationship("Trajet")
    gare = relationship("Gare")
    
    def __repr__(self):
        return f"<Horaire(trajet='{self.id_trajet}', gare='{self.id_gare}', ordre={self.ordre_arret})>"