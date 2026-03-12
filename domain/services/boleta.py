from typing import List, Optional
from domain.schemas.boleta import BoletaCreate, BoletaUpdate, BoletaResponse, BoletaListResponse
from persistencia.repositories.boleta import BoletaRepository


class BoletaService:
    def __init__(self, repository: BoletaRepository):
        self.repository = repository

    def crear_boleta(self, boleta_in: BoletaCreate) -> BoletaResponse:
        self._calcular_automatismos(boleta_in)
        db_boleta = self.repository.create(boleta_in)
        # Re-fetch con joins para incluir alumno y calificaciones.materia
        db_boleta = self.repository.get_by_id(db_boleta.id)
        return BoletaResponse.model_validate(db_boleta)

    def _calcular_automatismos(self, boleta_in: BoletaCreate):
        if not boleta_in.calificaciones:
            return

        total_def_final = 0
        sum_l1, count_l1 = 0, 0
        sum_l2, count_l2 = 0, 0
        sum_l3, count_l3 = 0, 0
        materias_numericas_count = 0

        for calif in boleta_in.calificaciones:
            lapsos = [
                calif.lapso_1_def,
                calif.lapso_2_def,
                calif.lapso_3_def
            ]
            valid_lapsos = [l for l in lapsos if l is not None]
            
            if valid_lapsos:
                # Calcular definitiva de la materia (promedio de los lapsos provistos)
                def_materia = sum(valid_lapsos) / len(valid_lapsos)
                calif.def_final = int(def_materia + 0.5) 
                
                total_def_final += calif.def_final
                materias_numericas_count += 1
            
            # Acumular para medias por lapso
            if calif.lapso_1_def is not None:
                sum_l1 += calif.lapso_1_def
                count_l1 += 1
            if calif.lapso_2_def is not None:
                sum_l2 += calif.lapso_2_def
                count_l2 += 1
            if calif.lapso_3_def is not None:
                sum_l3 += calif.lapso_3_def
                count_l3 += 1
        
        # Calcular medias por lapso
        if count_l1 > 0:
            boleta_in.media_lapso_1 = round(sum_l1 / count_l1, 2)
        if count_l2 > 0:
            boleta_in.media_lapso_2 = round(sum_l2 / count_l2, 2)
        if count_l3 > 0:
            boleta_in.media_lapso_3 = round(sum_l3 / count_l3, 2)
            
        if materias_numericas_count > 0:
            boleta_in.medias_globales = round(total_def_final / materias_numericas_count, 2)

    def obtener_boleta(self, boleta_id: int) -> Optional[BoletaResponse]:
        db_boleta = self.repository.get_by_id(boleta_id)
        if db_boleta:
            return BoletaResponse.model_validate(db_boleta)
        return None

    def listar_boletas(
        self,
        skip: int = 0,
        limit: int = 100,
        alumno_id: Optional[int] = None,
        anio_escolar: Optional[str] = None,
        tipo_evaluacion: Optional[str] = None,
    ) -> List[BoletaListResponse]:
        db_boletas = self.repository.get_all(
            skip=skip,
            limit=limit,
            alumno_id=alumno_id,
            anio_escolar=anio_escolar,
            tipo_evaluacion=tipo_evaluacion,
        )
        return [BoletaListResponse.model_validate(b) for b in db_boletas]

    def actualizar_boleta(self, boleta_id: int, boleta_in: BoletaUpdate) -> Optional[BoletaResponse]:
        db_boleta = self.repository.update(boleta_id, boleta_in)
        if db_boleta:
            return BoletaResponse.model_validate(db_boleta)
        return None

    def eliminar_boleta(self, boleta_id: int) -> bool:
        return self.repository.delete(boleta_id)
