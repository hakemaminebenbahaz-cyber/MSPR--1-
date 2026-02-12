from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Ligne(Base):
    __tablename__ = "lignes"
    
    id_ligne = Column(String(100), primary_key=True)
    id_operateur = Column(String(100), ForeignKey("operateurs.id_operateur"))
    code_ligne = Column(String(20), nullable=False)
    nom_complet_ligne = Column(String)
    type_transport = Column(Integer)
    couleur_ligne = Column(String(6))
    
    # Relation
    operateur = relationship("Operateur")
    
    def __repr__(self):
        return f"<Ligne(id='{self.id_ligne}', code='{self.code_ligne}')>"