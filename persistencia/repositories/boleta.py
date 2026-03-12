from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Optional
from persistencia.models import Boleta, Calificacion
from domain.schemas.boleta import BoletaCreate, BoletaUpdate


class BoletaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, boleta_in: BoletaCreate) -> Boleta:
        db_boleta = Boleta(
            alumno_id=boleta_in.alumno_id,
            anio_escolar=boleta_in.anio_escolar,
            grado=boleta_in.grado,
            seccion=boleta_in.seccion,
            numero_lista=boleta_in.numero_lista,
            tipo_evaluacion=boleta_in.tipo_evaluacion,
            observaciones=boleta_in.observaciones,
            media_lapso_1=boleta_in.media_lapso_1,
            media_lapso_2=boleta_in.media_lapso_2,
            media_lapso_3=boleta_in.media_lapso_3,
            medias_globales=boleta_in.medias_globales,
            profesor=boleta_in.profesor,
            nombre_plantel=boleta_in.nombre_plantel,
            direccion_plantel=boleta_in.direccion_plantel,
        )

        # Crear calificaciones asociadas
        for calif_in in boleta_in.calificaciones:
            db_calif = Calificacion(
                materia_id=calif_in.materia_id,
                lapso_1_def=calif_in.lapso_1_def,
                lapso_2_def=calif_in.lapso_2_def,
                lapso_3_def=calif_in.lapso_3_def,
                def_final=calif_in.def_final,
                literal=calif_in.literal,
            )
            db_boleta.calificaciones.append(db_calif)

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
                joinedload(Boleta.calificaciones).joinedload(Calificacion.materia),
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
