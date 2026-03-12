from pydantic import BaseModel
from typing import Optional


# Propiedades base
class TareaBase(BaseModel):
    titulo: str
    contenido: Optional[str] = None
    completada: bool = False


# Recibir al crear
class TareaCreate(TareaBase):
    pass


# Recibir al actualizar
class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    completada: Optional[bool] = None


# Retornar al cliente
class TareaResponse(TareaBase):
    id: int

    model_config = {
        "from_attributes": True
    }
