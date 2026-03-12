from pydantic import BaseModel
from typing import Optional
from domain.schemas.materia import MateriaResponse


class CalificacionBase(BaseModel):
    alumno_id: int
    materia_id: int
    anio_escolar: str
    lapso_1_def: Optional[int] = None
    lapso_2_def: Optional[int] = None
    lapso_3_def: Optional[int] = None
    def_final: Optional[int] = None
    literal: Optional[str] = None


class CalificacionCreate(CalificacionBase):
    pass


class CalificacionUpdate(BaseModel):
    lapso_1_def: Optional[int] = None
    lapso_2_def: Optional[int] = None
    lapso_3_def: Optional[int] = None
    def_final: Optional[int] = None
    literal: Optional[str] = None


# --- NUEVO: Entrada Simplificada ---
class LapsoNotaInput(BaseModel):
    alumno_id: int
    materia_id: int
    lapso: int  # 1, 2 o 3
    nota: int   # 0 a 20
    anio_escolar: Optional[str] = None # Si es None, usar el actual de config
    literal: Optional[str] = None


class CalificacionResponse(CalificacionBase):
    id: int
    materia: MateriaResponse

    model_config = {
        "from_attributes": True
    }
