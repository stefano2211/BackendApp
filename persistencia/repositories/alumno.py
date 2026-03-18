from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from persistencia.models import Alumno
from domain.schemas.alumno import AlumnoCreate, AlumnoUpdate


class AlumnoRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        stmt = select(func.count()).select_from(Alumno)
        return self.session.scalars(stmt).first() or 0

    def create(self, alumno_in: AlumnoCreate) -> Alumno:
        db_alumno = Alumno(**alumno_in.model_dump())
        self.session.add(db_alumno)
        self.session.commit()
        self.session.refresh(db_alumno)
        return db_alumno

    def get_by_id(self, alumno_id: int) -> Optional[Alumno]:
        stmt = select(Alumno).where(Alumno.id == alumno_id)
        return self.session.scalars(stmt).first()

    def get_by_cedula(self, cedula: str) -> Optional[Alumno]:
        stmt = select(Alumno).where(Alumno.cedula == cedula)
        return self.session.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Alumno]:
        stmt = select(Alumno).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, alumno_id: int, alumno_in: AlumnoUpdate) -> Optional[Alumno]:
        db_alumno = self.get_by_id(alumno_id)
        if not db_alumno:
            return None

        update_data = alumno_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_alumno, key, value)

        self.session.commit()
        self.session.refresh(db_alumno)
        return db_alumno

    def delete(self, alumno_id: int) -> bool:
        db_alumno = self.get_by_id(alumno_id)
        if not db_alumno:
            return False

        self.session.delete(db_alumno)
        self.session.commit()
        return True
