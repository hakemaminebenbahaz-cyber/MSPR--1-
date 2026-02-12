from sqlalchemy import Column, String
from core.database import Base

class Operateur(Base):
    __tablename__ = "operateurs"
    
    id_operateur = Column(String(100), primary_key=True)
    nom_operateur = Column(String(200), nullable=False)
    site_web = Column(String(500))
    fuseau_horaire = Column(String(50))
    langue = Column(String(2))
    
    def __repr__(self):
        return f"<Operateur(id='{self.id_operateur}', nom='{self.nom_operateur}')>"