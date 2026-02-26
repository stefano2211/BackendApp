from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base

class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    contenido = Column(String, nullable=True)
    completada = Column(Boolean, default=False)
