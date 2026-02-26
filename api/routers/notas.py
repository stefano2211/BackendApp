from typing import List
from fastapi import APIRouter, Depends, HTTPException

from domain.schemas import NotaCreate, NotaUpdate, NotaResponse
from domain.services import NotaService
from api.deps import get_nota_service

router = APIRouter()

@router.post("/", response_model=NotaResponse, status_code=201)
def create_nota(
    nota_in: NotaCreate,
    service: NotaService = Depends(get_nota_service)
) -> NotaResponse:
    return service.crear_nota(nota_in)

@router.get("/", response_model=List[NotaResponse])
def read_notas(
    skip: int = 0,
    limit: int = 100,
    service: NotaService = Depends(get_nota_service)
) -> List[NotaResponse]:
    return service.listar_notas(skip=skip, limit=limit)

@router.get("/{nota_id}", response_model=NotaResponse)
def read_nota(
    nota_id: int,
    service: NotaService = Depends(get_nota_service)
) -> NotaResponse:
    nota = service.obtener_nota(nota_id)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return nota

@router.put("/{nota_id}", response_model=NotaResponse)
def update_nota(
    nota_id: int,
    nota_in: NotaUpdate,
    service: NotaService = Depends(get_nota_service)
) -> NotaResponse:
    nota = service.actualizar_nota(nota_id, nota_in)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return nota

@router.delete("/{nota_id}", status_code=204)
def delete_nota(
    nota_id: int,
    service: NotaService = Depends(get_nota_service)
):
    success = service.eliminar_nota(nota_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
