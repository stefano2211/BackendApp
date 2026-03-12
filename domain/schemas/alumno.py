from pydantic import BaseModel
from typing import Optional
from datetime import date


class AlumnoBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    codigo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    estado_nacimiento: Optional[str] = None
    nombre_representante: Optional[str] = None
    direccion_representante: Optional[str] = None
    grado: Optional[int] = None
    seccion: Optional[str] = None


class AlumnoCreate(AlumnoBase):
    pass


class AlumnoUpdate(BaseModel):
    cedula: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    codigo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = None
    estado_nacimiento: Optional[str] = None
    nombre_representante: Optional[str] = None
    direccion_representante: Optional[str] = None


class AlumnoResponse(AlumnoBase):
    id: int

    model_config = {
        "from_attributes": True
    }
