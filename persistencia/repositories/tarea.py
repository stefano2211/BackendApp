from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from persistencia.models import Tarea
from domain.schemas.tarea import TareaCreate, TareaUpdate


class TareaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tarea_in: TareaCreate) -> Tarea:
        db_tarea = Tarea(
            titulo=tarea_in.titulo,
            contenido=tarea_in.contenido,
            completada=tarea_in.completada
        )
        self.session.add(db_tarea)
        self.session.commit()
        self.session.refresh(db_tarea)
        return db_tarea

    def get_by_id(self, tarea_id: int) -> Optional[Tarea]:
        stmt = select(Tarea).where(Tarea.id == tarea_id)
        return self.session.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Tarea]:
        stmt = select(Tarea).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, tarea_id: int, tarea_in: TareaUpdate) -> Optional[Tarea]:
        db_tarea = self.get_by_id(tarea_id)
        if not db_tarea:
            return None

        update_data = tarea_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_tarea, key, value)

        self.session.commit()
        self.session.refresh(db_tarea)
        return db_tarea

    def delete(self, tarea_id: int) -> bool:
        db_tarea = self.get_by_id(tarea_id)
        if not db_tarea:
            return False

        self.session.delete(db_tarea)
        self.session.commit()
        return True
