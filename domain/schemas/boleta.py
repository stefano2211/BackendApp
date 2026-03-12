from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from domain.schemas.alumno import AlumnoResponse
from domain.schemas.materia import MateriaResponse


# --- Calificacion Schemas ---

class CalificacionBase(BaseModel):
    materia_id: int
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


class CalificacionResponse(CalificacionBase):
    id: int
    materia: MateriaResponse

    model_config = {
        "from_attributes": True
    }


# --- Boleta Schemas ---

class BoletaBase(BaseModel):
    alumno_id: int
    anio_escolar: str
    grado: int
    seccion: str
    numero_lista: Optional[int] = None
    tipo_evaluacion: str
    observaciones: Optional[str] = None
    media_lapso_1: Optional[float] = None
    media_lapso_2: Optional[float] = None
    media_lapso_3: Optional[float] = None
    medias_globales: Optional[float] = None
    profesor: Optional[str] = None
    nombre_plantel: Optional[str] = None
    direccion_plantel: Optional[str] = None


class BoletaCreate(BoletaBase):
    calificaciones: List[CalificacionCreate] = []


class BoletaUpdate(BaseModel):
    anio_escolar: Optional[str] = None
    grado: Optional[int] = None
    seccion: Optional[str] = None
    numero_lista: Optional[int] = None
    tipo_evaluacion: Optional[str] = None
    observaciones: Optional[str] = None
    media_lapso_1: Optional[float] = None
    media_lapso_2: Optional[float] = None
    media_lapso_3: Optional[float] = None
    medias_globales: Optional[float] = None
    profesor: Optional[str] = None
    nombre_plantel: Optional[str] = None
    direccion_plantel: Optional[str] = None


class BoletaResponse(BoletaBase):
    id: int
    created_at: Optional[datetime] = None
    alumno: AlumnoResponse
    calificaciones: List[CalificacionResponse] = []

    model_config = {
        "from_attributes": True
    }


class BoletaListResponse(BoletaBase):
    """Response sin calificaciones anidadas, para listados."""
    id: int
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
