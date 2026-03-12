from typing import List
from fastapi import APIRouter, Depends, HTTPException

from domain.schemas.tarea import TareaCreate, TareaUpdate, TareaResponse
from domain.services.tarea import TareaService
from api.deps import get_tarea_service

router = APIRouter()


@router.post("/", response_model=TareaResponse, status_code=201)
def create_tarea(
    tarea_in: TareaCreate,
    service: TareaService = Depends(get_tarea_service)
) -> TareaResponse:
    return service.crear_tarea(tarea_in)


@router.get("/", response_model=List[TareaResponse])
def read_tareas(
    skip: int = 0,
    limit: int = 100,
    service: TareaService = Depends(get_tarea_service)
) -> List[TareaResponse]:
    return service.listar_tareas(skip=skip, limit=limit)


@router.get("/{tarea_id}", response_model=TareaResponse)
def read_tarea(
    tarea_id: int,
    service: TareaService = Depends(get_tarea_service)
) -> TareaResponse:
    tarea = service.obtener_tarea(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@router.put("/{tarea_id}", response_model=TareaResponse)
def update_tarea(
    tarea_id: int,
    tarea_in: TareaUpdate,
    service: TareaService = Depends(get_tarea_service)
) -> TareaResponse:
    tarea = service.actualizar_tarea(tarea_id, tarea_in)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@router.delete("/{tarea_id}", status_code=204)
def delete_tarea(
    tarea_id: int,
    service: TareaService = Depends(get_tarea_service)
):
    success = service.eliminar_tarea(tarea_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
