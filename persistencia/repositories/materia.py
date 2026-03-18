from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from persistencia.models import Materia
from domain.schemas.materia import MateriaCreate, MateriaUpdate


class MateriaRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        stmt = select(func.count()).select_from(Materia)
        return self.session.scalars(stmt).first() or 0

    def create(self, materia_in: MateriaCreate) -> Materia:
        db_materia = Materia(
            nombre=materia_in.nombre,
            grado=materia_in.grado,
            es_numerica=materia_in.es_numerica,
        )
        self.session.add(db_materia)
        self.session.commit()
        self.session.refresh(db_materia)
        return db_materia

    def get_by_id(self, materia_id: int) -> Optional[Materia]:
        stmt = select(Materia).where(Materia.id == materia_id)
        return self.session.scalars(stmt).first()

    def get_by_grado(self, grado: int) -> List[Materia]:
        stmt = select(Materia).where(Materia.grado == grado)
        return list(self.session.scalars(stmt).all())

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Materia]:
        stmt = select(Materia).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, materia_id: int, materia_in: MateriaUpdate) -> Optional[Materia]:
        db_materia = self.get_by_id(materia_id)
        if not db_materia:
            return None

        update_data = materia_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_materia, key, value)

        self.session.commit()
        self.session.refresh(db_materia)
        return db_materia

    def delete(self, materia_id: int) -> bool:
        db_materia = self.get_by_id(materia_id)
        if not db_materia:
            return False

        self.session.delete(db_materia)
        self.session.commit()
        return True
