from fastapi import APIRouter, Depends
from pydantic import BaseModel

from domain.services.alumno import AlumnoService
from domain.services.materia import MateriaService
from domain.services.boleta import BoletaService
from api.deps import (
    get_alumno_service,
    get_materia_service,
    get_boleta_service,
    get_current_user,
)
from persistencia.models import User

router = APIRouter()


class DashboardStatsResponse(BaseModel):
    total_alumnos: int
    total_materias: int
    total_boletas: int


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    alumno_service: AlumnoService = Depends(get_alumno_service),
    materia_service: MateriaService = Depends(get_materia_service),
    boleta_service: BoletaService = Depends(get_boleta_service),
    current_user: User = Depends(get_current_user),
) -> DashboardStatsResponse:
    """Obtiene estadísticas para el dashboard."""
    return DashboardStatsResponse(
        total_alumnos=alumno_service.contar_alumnos(),
        total_materias=materia_service.contar_materias(),
        total_boletas=boleta_service.contar_boletas(),
    )
