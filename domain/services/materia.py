from typing import List, Optional
from domain.schemas.materia import MateriaCreate, MateriaUpdate, MateriaResponse
from persistencia.repositories.materia import MateriaRepository


class MateriaService:
    def __init__(self, repository: MateriaRepository):
        self.repository = repository

    def contar_materias(self) -> int:
        return self.repository.count()

    def crear_materia(self, materia_in: MateriaCreate) -> MateriaResponse:
        db_materia = self.repository.create(materia_in)
        return MateriaResponse.model_validate(db_materia)

    def obtener_materia(self, materia_id: int) -> Optional[MateriaResponse]:
        db_materia = self.repository.get_by_id(materia_id)
        if db_materia:
            return MateriaResponse.model_validate(db_materia)
        return None

    def listar_materias(self, skip: int = 0, limit: int = 100) -> List[MateriaResponse]:
        db_materias = self.repository.get_all(skip=skip, limit=limit)
        return [MateriaResponse.model_validate(m) for m in db_materias]

    def listar_materias_por_grado(self, grado: int) -> List[MateriaResponse]:
        db_materias = self.repository.get_by_grado(grado)
        return [MateriaResponse.model_validate(m) for m in db_materias]

    def actualizar_materia(self, materia_id: int, materia_in: MateriaUpdate) -> Optional[MateriaResponse]:
        db_materia = self.repository.update(materia_id, materia_in)
        if db_materia:
            return MateriaResponse.model_validate(db_materia)
        return None

    def eliminar_materia(self, materia_id: int) -> bool:
        return self.repository.delete(materia_id)
