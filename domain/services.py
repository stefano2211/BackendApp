from typing import List, Optional
from domain.schemas import NotaCreate, NotaUpdate, NotaResponse
from persistencia.repository import NotaRepository

class NotaService:
    def __init__(self, repository: NotaRepository):
        self.repository = repository

    def crear_nota(self, nota_in: NotaCreate) -> NotaResponse:
        db_nota = self.repository.create(nota_in)
        return NotaResponse.model_validate(db_nota)

    def obtener_nota(self, nota_id: int) -> Optional[NotaResponse]:
        db_nota = self.repository.get_by_id(nota_id)
        if db_nota:
            return NotaResponse.model_validate(db_nota)
        return None

    def listar_notas(self, skip: int = 0, limit: int = 100) -> List[NotaResponse]:
        db_notas = self.repository.get_all(skip=skip, limit=limit)
        return [NotaResponse.model_validate(n) for n in db_notas]

    def actualizar_nota(self, nota_id: int, nota_in: NotaUpdate) -> Optional[NotaResponse]:
        db_nota = self.repository.update(nota_id, nota_in)
        if db_nota:
             return NotaResponse.model_validate(db_nota)
        return None

    def eliminar_nota(self, nota_id: int) -> bool:
        return self.repository.delete(nota_id)
