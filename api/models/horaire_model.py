from sqlalchemy import Column, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Horaire(Base):
    __tablename__ = "horaires"
    
    id_trajet = Column(String(100), ForeignKey("trajets.id_trajet"), primary_key=True)
    heure_depart = Column(Time)
    heure_arrivee = Column(Time)
    gare_depart = Column(String(100), primary_key=True)
    gare_arrivee = Column(String(100))
    
    def __repr__(self):
        return f"<Horaire(trajet='{self.id_trajet}', depart='{self.gare_depart}')>"