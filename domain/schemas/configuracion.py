from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfiguracionBase(BaseModel):
    nombre_plantel: Optional[str] = "U.E. Colegio Simón Bolívar"
    direccion_plantel: Optional[str] = "Calle Principal #45, Valencia"
    anio_escolar_actual: Optional[str] = "2024-2025"
    profesor_guia_default: Optional[str] = "Lic. Antonio Machado"


class ConfiguracionUpdate(ConfiguracionBase):
    pass


class ConfiguracionResponse(ConfiguracionBase):
    id: int
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
