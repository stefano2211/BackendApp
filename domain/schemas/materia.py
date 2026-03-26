from pydantic import BaseModel
from typing import Optional


class MateriaBase(BaseModel):
    nombre: str
    grado: int
    es_numerica: bool = True
    modalidad: Optional[str] = "Media General"


class MateriaCreate(MateriaBase):
    pass


class MateriaUpdate(BaseModel):
    nombre: Optional[str] = None
    grado: Optional[int] = None
    es_numerica: Optional[bool] = None
    modalidad: Optional[str] = None


class MateriaResponse(MateriaBase):
    id: int

    model_config = {
        "from_attributes": True
    }
