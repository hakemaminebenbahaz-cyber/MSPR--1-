from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from core.database import Base

class LigneTrain(Base):
    __tablename__ = "lignes_train"
    
    id_ligne = Column(String(100), primary_key=True)
    id_operateur = Column(String(100))
    code_ligne = Column(String(20), nullable=False)
    nom_complet_ligne = Column(String)
    type_transport = Column(Integer)
    couleur_ligne = Column(String(6))
    
    def __repr__(self):
        return f"<LigneTrain(id='{self.id_ligne}', code='{self.code_ligne}')>"