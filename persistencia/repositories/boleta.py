from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Optional
from persistencia.models import Boleta, Calificacion
from domain.schemas.boleta import BoletaCreate, BoletaUpdate


class BoletaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, boleta_in: BoletaCreate) -> Boleta:
        # Usar model_dump para evitar mapeo manual propenso a errores
        data = boleta_in.model_dump()
        db_boleta = Boleta(**data)

        self.session.add(db_boleta)
        self.session.commit()
        self.session.refresh(db_boleta)
        return db_boleta

    def get_by_id(self, boleta_id: int) -> Optional[Boleta]:
        stmt = (
            select(Boleta)
            .where(Boleta.id == boleta_id)
            .options(
                joinedload(Boleta.alumno),
            )
        )
        return self.session.scalars(stmt).first()

    def get_by_alumno(
        self,
        alumno_id: int,
        anio_escolar: Optional[str] = None,
        tipo_evaluacion: Optional[str] = None,
    ) -> List[Boleta]:
        stmt = select(Boleta).where(Boleta.alumno_id == alumno_id)

        if anio_escolar:
            stmt = stmt.where(Boleta.anio_escolar == anio_escolar)
        if tipo_evaluacion:
            stmt = stmt.where(Boleta.tipo_evaluacion == tipo_evaluacion)

        return list(self.session.scalars(stmt).all())

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        alumno_id: Optional[int] = None,
        anio_escolar: Optional[str] = None,
        tipo_evaluacion: Optional[str] = None,
    ) -> List[Boleta]:
        stmt = select(Boleta)

        if alumno_id:
            stmt = stmt.where(Boleta.alumno_id == alumno_id)
        if anio_escolar:
            stmt = stmt.where(Boleta.anio_escolar == anio_escolar)
        if tipo_evaluacion:
            stmt = stmt.where(Boleta.tipo_evaluacion == tipo_evaluacion)

        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, boleta_id: int, boleta_in: BoletaUpdate) -> Optional[Boleta]:
        db_boleta = self.get_by_id(boleta_id)
        if not db_boleta:
            return None

        update_data = boleta_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_boleta, key, value)

        self.session.commit()
        self.session.refresh(db_boleta)
        return db_boleta

    def delete(self, boleta_id: int) -> bool:
        db_boleta = self.get_by_id(boleta_id)
        if not db_boleta:
            return False

        self.session.delete(db_boleta)
        self.session.commit()
        return True
