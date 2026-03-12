from typing import List
from fastapi import APIRouter, Depends, HTTPException

from domain.schemas.calificacion import CalificacionCreate, CalificacionUpdate, CalificacionResponse, LapsoNotaInput
from domain.services.calificacion import CalificacionService
from api.deps import get_calificacion_service

router = APIRouter()


@router.post("/", response_model=CalificacionResponse, status_code=201)
def registrar_nota_rapida(
    calif_in: LapsoNotaInput,
    service: CalificacionService = Depends(get_calificacion_service)
) -> CalificacionResponse:
    """Registra una nota de un lapso específico de forma simplificada."""
    return service.registrar_lapso_nota(calif_in)


@router.get("/alumno/{alumno_id}", response_model=List[CalificacionResponse])
def listar_calificaciones_alumno(
    alumno_id: int,
    anio_escolar: str,
    service: CalificacionService = Depends(get_calificacion_service)
) -> List[CalificacionResponse]:
    return service.listar_por_alumno(alumno_id, anio_escolar)


@router.get("/{calif_id}", response_model=CalificacionResponse)
def read_calificacion(
    calif_id: int,
    service: CalificacionService = Depends(get_calificacion_service)
) -> CalificacionResponse:
    calif = service.obtener_calificacion(calif_id)
    if not calif:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    return calif


@router.put("/{calif_id}", response_model=CalificacionResponse)
def update_calificacion(
    calif_id: int,
    calif_in: CalificacionUpdate,
    service: CalificacionService = Depends(get_calificacion_service)
) -> CalificacionResponse:
    calif = service.actualizar_calificacion(calif_id, calif_in)
    if not calif:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    return calif


@router.delete("/{calif_id}", status_code=204)
def delete_calificacion(
    calif_id: int,
    service: CalificacionService = Depends(get_calificacion_service)
):
    success = service.eliminar_calificacion(calif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
