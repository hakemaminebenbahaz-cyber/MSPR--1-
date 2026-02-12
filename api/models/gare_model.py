from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Gare(Base):
    __tablename__ = "gares"
    
    id_gare = Column(String(100), primary_key=True)
    nom_gare = Column(String(200), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    gare_parente = Column(String(100), ForeignKey("gares.id_gare"))
    
    # Auto-référence
    parent = relationship("Gare", remote_side=[id_gare])
    
    def __repr__(self):
        return f"<Gare(id='{self.id_gare}', nom='{self.nom_gare}')>"