from pydantic import BaseModel
from typing import Optional

# Base Properties
class NotaBase(BaseModel):
    titulo: str
    contenido: Optional[str] = None
    completada: bool = False

# Properties to receive on creation
class NotaCreate(NotaBase):
    pass

# Properties to receive on update
class NotaUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    completada: Optional[bool] = None

# Properties to return to client
class NotaResponse(NotaBase):
    id: int

    model_config = {
        "from_attributes": True # Equivalente a orm_mode = True en v1
    }
