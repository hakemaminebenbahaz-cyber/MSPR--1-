from sqlalchemy import Column, Integer
from core.database import Base

class CalendrierCirculation(Base):
    __tablename__ = "calendrier_circulation"
    
    id_service = Column(Integer, primary_key=True)
    date_circulation = Column(Integer, primary_key=True)
    type_exception = Column(Integer)
    
    def __repr__(self):
        return f"<Calendrier(service={self.id_service}, date={self.date_circulation})>"