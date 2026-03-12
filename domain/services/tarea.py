from typing import List, Optional
from domain.schemas.tarea import TareaCreate, TareaUpdate, TareaResponse
from persistencia.repositories.tarea import TareaRepository


class TareaService:
    def __init__(self, repository: TareaRepository):
        self.repository = repository

    def crear_tarea(self, tarea_in: TareaCreate) -> TareaResponse:
        db_tarea = self.repository.create(tarea_in)
        return TareaResponse.model_validate(db_tarea)

    def obtener_tarea(self, tarea_id: int) -> Optional[TareaResponse]:
        db_tarea = self.repository.get_by_id(tarea_id)
        if db_tarea:
            return TareaResponse.model_validate(db_tarea)
        return None

    def listar_tareas(self, skip: int = 0, limit: int = 100) -> List[TareaResponse]:
        db_tareas = self.repository.get_all(skip=skip, limit=limit)
        return [TareaResponse.model_validate(n) for n in db_tareas]

    def actualizar_tarea(self, tarea_id: int, tarea_in: TareaUpdate) -> Optional[TareaResponse]:
        db_tarea = self.repository.update(tarea_id, tarea_in)
        if db_tarea:
            return TareaResponse.model_validate(db_tarea)
        return None

    def eliminar_tarea(self, tarea_id: int) -> bool:
        return self.repository.delete(tarea_id)
