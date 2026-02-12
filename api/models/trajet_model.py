from sqlalchemy import Column, String, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from core.database import Base

class Trajet(Base):
    __tablename__ = "trajets"
    
    id_trajet = Column(String(100), primary_key=True)
    id_ligne = Column(String(100), ForeignKey("lignes.id_ligne"))
    id_service = Column(Integer)
    date_circulation = Column(Integer)
    destination_affichee = Column(String(50))
    sens_circulation = Column(Integer)
    
    # Relations
    ligne = relationship("Ligne")
    
    __table_args__ = (
        ForeignKeyConstraint(
            ['id_service', 'date_circulation'],
            ['calendrier_circulation.id_service', 'calendrier_circulation.date_circulation']
        ),
    )
    
    def __repr__(self):
        return f"<Trajet(id='{self.id_trajet}', destination='{self.destination_affichee}')>"