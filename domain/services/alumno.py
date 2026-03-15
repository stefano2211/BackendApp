from typing import List, Optional
from domain.schemas.alumno import AlumnoCreate, AlumnoUpdate, AlumnoResponse
from persistencia.repositories.alumno import AlumnoRepository


class AlumnoService:
    def __init__(self, repository: AlumnoRepository):
        self.repository = repository

    def contar_alumnos(self) -> int:
        return self.repository.count()

    def crear_alumno(self, alumno_in: AlumnoCreate) -> AlumnoResponse:
        db_alumno = self.repository.create(alumno_in)
        return AlumnoResponse.model_validate(db_alumno)

    def obtener_alumno(self, alumno_id: int) -> Optional[AlumnoResponse]:
        db_alumno = self.repository.get_by_id(alumno_id)
        if db_alumno:
            return AlumnoResponse.model_validate(db_alumno)
        return None

    def obtener_alumno_por_cedula(self, cedula: str) -> Optional[AlumnoResponse]:
        db_alumno = self.repository.get_by_cedula(cedula)
        if db_alumno:
            return AlumnoResponse.model_validate(db_alumno)
        return None

    def listar_alumnos(self, skip: int = 0, limit: int = 100) -> List[AlumnoResponse]:
        db_alumnos = self.repository.get_all(skip=skip, limit=limit)
        return [AlumnoResponse.model_validate(a) for a in db_alumnos]

    def actualizar_alumno(self, alumno_id: int, alumno_in: AlumnoUpdate) -> Optional[AlumnoResponse]:
        db_alumno = self.repository.update(alumno_id, alumno_in)
        if db_alumno:
            return AlumnoResponse.model_validate(db_alumno)
        return None

    def eliminar_alumno(self, alumno_id: int) -> bool:
        return self.repository.delete(alumno_id)
