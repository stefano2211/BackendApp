from typing import List, Optional
from domain.schemas.calificacion import CalificacionCreate, CalificacionUpdate, CalificacionResponse, LapsoNotaInput
from persistencia.repositories.calificacion import CalificacionRepository
from persistencia.repositories.configuracion import ConfiguracionRepository


class CalificacionService:
    def __init__(self, repository: CalificacionRepository, config_repo: ConfiguracionRepository):
        self.repository = repository
        self.config_repo = config_repo

    def registrar_lapso_nota(self, input_data: LapsoNotaInput) -> CalificacionResponse:
        # 1. Obtener año escolar si no se provee
        anio_escolar = input_data.anio_escolar
        if not anio_escolar:
            config = self.config_repo.get_config()
            anio_escolar = config.anio_escolar_actual if config else "2024-2025"

        # 2. Buscar registro existente
        existente = self.repository.get_by_alumno_materia_year(
            input_data.alumno_id, input_data.materia_id, anio_escolar
        )

        if existente:
            # Actualizar lapso específico
            update_data = CalificacionUpdate()
            if input_data.lapso == 1: update_data.lapso_1_def = input_data.nota
            elif input_data.lapso == 2: update_data.lapso_2_def = input_data.nota
            elif input_data.lapso == 3: update_data.lapso_3_def = input_data.nota
            
            if input_data.literal: update_data.literal = input_data.literal
            
            # Recalcular definitiva interna
            self._pre_calcular_definitiva_sql(existente, update_data)
            
            db_calif = self.repository.update(existente.id, update_data)
        else:
            # Crear nuevo
            create_data = CalificacionCreate(
                alumno_id=input_data.alumno_id,
                materia_id=input_data.materia_id,
                anio_escolar=anio_escolar,
                literal=input_data.literal
            )
            if input_data.lapso == 1: create_data.lapso_1_def = input_data.nota
            elif input_data.lapso == 2: create_data.lapso_2_def = input_data.nota
            elif input_data.lapso == 3: create_data.lapso_3_def = input_data.nota
            
            self._calcular_definitiva(create_data)
            db_calif = self.repository.create(create_data)

        return CalificacionResponse.model_validate(self.repository.get_by_id(db_calif.id))

    def _pre_calcular_definitiva_sql(self, db_obj, update_data):
        l1 = update_data.lapso_1_def if update_data.lapso_1_def is not None else db_obj.lapso_1_def
        l2 = update_data.lapso_2_def if update_data.lapso_2_def is not None else db_obj.lapso_2_def
        l3 = update_data.lapso_3_def if update_data.lapso_3_def is not None else db_obj.lapso_3_def
        
        valid = [v for v in [l1, l2, l3] if v is not None]
        if valid:
            update_data.def_final = int((sum(valid) / len(valid)) + 0.5)

    def registrar_calificacion(self, calif_in: CalificacionCreate) -> CalificacionResponse:
        if not calif_in.anio_escolar:
            config = self.config_repo.get_config()
            calif_in.anio_escolar = config.anio_escolar_actual if config else "2024-2025"
            
        self._calcular_definitiva(calif_in)
        # Verificar si ya existe para actualizar o crear
        existente = self.repository.get_by_alumno_materia_year(
            calif_in.alumno_id, calif_in.materia_id, calif_in.anio_escolar
        )
        if existente:
            update_data = CalificacionUpdate(**calif_in.model_dump(exclude_unset=True))
            db_calif = self.repository.update(existente.id, update_data)
        else:
            db_calif = self.repository.create(calif_in)
        
        # Re-fetch con materia
        db_calif = self.repository.get_by_id(db_calif.id)
        return CalificacionResponse.model_validate(db_calif)

    def _calcular_definitiva(self, calif: CalificacionCreate | CalificacionUpdate):
        lapsos = [calif.lapso_1_def, calif.lapso_2_def, calif.lapso_3_def]
        valid_lapsos = [l for l in lapsos if l is not None]
        if valid_lapsos:
            calif.def_final = int((sum(valid_lapsos) / len(valid_lapsos)) + 0.5)

    def obtener_calificacion(self, calif_id: int) -> Optional[CalificacionResponse]:
        db_calif = self.repository.get_by_id(calif_id)
        if db_calif:
            return CalificacionResponse.model_validate(db_calif)
        return None

    def listar_por_alumno(self, alumno_id: int, anio_escolar: Optional[str] = None) -> List[CalificacionResponse]:
        if not anio_escolar:
            config = self.config_repo.get_config()
            anio_escolar = config.anio_escolar_actual if config else "2024-2025"
            
        db_califs = self.repository.get_all_by_alumno_year(alumno_id, anio_escolar)
        return [CalificacionResponse.model_validate(c) for c in db_califs]

    def actualizar_calificacion(self, calif_id: int, calif_in: CalificacionUpdate) -> Optional[CalificacionResponse]:
        db_calif = self.repository.update(calif_id, calif_in)
        if db_calif:
            return CalificacionResponse.model_validate(db_calif)
        return None

    def eliminar_calificacion(self, calif_id: int) -> bool:
        return self.repository.delete(calif_id)
