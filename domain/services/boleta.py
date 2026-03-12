from typing import List, Optional
from domain.schemas.boleta import BoletaCreate, BoletaUpdate, BoletaResponse, BoletaListResponse
from domain.schemas.calificacion import CalificacionResponse
from persistencia.repositories.boleta import BoletaRepository
from persistencia.repositories.calificacion import CalificacionRepository
from persistencia.repositories.configuracion import ConfiguracionRepository
from persistencia.repositories.alumno import AlumnoRepository


class BoletaService:
    def __init__(
        self, 
        repository: BoletaRepository, 
        calif_repo: CalificacionRepository,
        config_repo: ConfiguracionRepository,
        alumno_repo: AlumnoRepository
    ):
        self.repository = repository
        self.calif_repo = calif_repo
        self.config_repo = config_repo
        self.alumno_repo = alumno_repo

    def crear_boleta(self, boleta_in: BoletaCreate) -> BoletaResponse:
        try:
            # 1. Obtener Configuración y Alumno para autocompletar
            config = self.config_repo.get_config()
            alumno = self.alumno_repo.get_by_id(boleta_in.alumno_id)
            
            # 2. Llenar campos faltantes desde Configuración
            if config:
                if not boleta_in.anio_escolar: boleta_in.anio_escolar = config.anio_escolar_actual
                if not boleta_in.nombre_plantel: boleta_in.nombre_plantel = config.nombre_plantel
                if not boleta_in.direccion_plantel: boleta_in.direccion_plantel = config.direccion_plantel
                if not boleta_in.profesor: boleta_in.profesor = config.profesor_guia_default
                
            # 3. Llenar campos faltantes desde Alumno (grado/seccion)
            if alumno:
                if boleta_in.grado is None: boleta_in.grado = alumno.grado if alumno.grado else 1
                if boleta_in.seccion is None: boleta_in.seccion = alumno.seccion if alumno.seccion else "A"
            
            # 4. Fallback final para evitar IntegrityError
            if boleta_in.grado is None: boleta_in.grado = 1
            if boleta_in.seccion is None: boleta_in.seccion = "A"
            if not boleta_in.anio_escolar: boleta_in.anio_escolar = "2024-2025"
            if not boleta_in.tipo_evaluacion: boleta_in.tipo_evaluacion = "Final de Lapso"

            # 5. Buscar las calificaciones existentes para este alumno y año
            calificaciones_db = self.calif_repo.get_all_by_alumno_year(
                boleta_in.alumno_id, boleta_in.anio_escolar
            )
            
            # 6. Calcular promedios basados en la DB
            self._calcular_automatismos_db(boleta_in, calificaciones_db)
            
            # 7. Guardar la boleta
            db_boleta = self.repository.create(boleta_in)
            
            # 8. Re-fetch con joins
            db_boleta = self.repository.get_by_id(db_boleta.id)
            
            # Mapear respuesta incluyendo las calificaciones encontradas
            response = BoletaResponse.model_validate(db_boleta)
            # Inyectamos las calificaciones encontradas mapeadas a Schema
            response.calificaciones = [
                CalificacionResponse.model_validate(c) for c in calificaciones_db
            ]
            
            return response
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR IN crear_boleta: {e}")
            traceback.print_exc()
            raise e

    def _calcular_automatismos_db(self, boleta_in: BoletaCreate, calificaciones: List):
        if not calificaciones:
            return

        total_def_final = 0
        sum_l1, count_l1 = 0, 0
        sum_l2, count_l2 = 0, 0
        sum_l3, count_l3 = 0, 0
        materias_numericas_count = 0

        for calif in calificaciones:
            es_numerica = calif.materia.es_numerica if calif.materia else True

            lapsos = [
                calif.lapso_1_def,
                calif.lapso_2_def,
                calif.lapso_3_def
            ]
            valid_lapsos = [l for l in lapsos if l is not None]
            
            if valid_lapsos:
                if calif.def_final is not None:
                    if es_numerica:
                        total_def_final += calif.def_final
                        materias_numericas_count += 1
            
            if es_numerica:
                if calif.lapso_1_def is not None:
                    sum_l1 += calif.lapso_1_def
                    count_l1 += 1
                if calif.lapso_2_def is not None:
                    sum_l2 += calif.lapso_2_def
                    count_l2 += 1
                if calif.lapso_3_def is not None:
                    sum_l3 += calif.lapso_3_def
                    count_l3 += 1
        
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
            response = BoletaResponse.model_validate(db_boleta)
            califs = self.calif_repo.get_all_by_alumno_year(
                db_boleta.alumno_id, db_boleta.anio_escolar
            )
            response.calificaciones = [
                CalificacionResponse.model_validate(c) for c in califs
            ]
            return response
        return None

    def listar_boletas(self, skip: int = 0, limit: int = 100, **kwargs) -> List[BoletaListResponse]:
        db_boletas = self.repository.get_all(skip=skip, limit=limit, **kwargs)
        return [BoletaListResponse.model_validate(b) for b in db_boletas]

    def actualizar_boleta(self, boleta_id: int, boleta_in: BoletaUpdate) -> Optional[BoletaResponse]:
        db_boleta = self.repository.update(boleta_id, boleta_in)
        if db_boleta:
            return self.obtener_boleta(db_boleta.id)
        return None

    def eliminar_boleta(self, boleta_id: int) -> bool:
        return self.repository.delete(boleta_id)
