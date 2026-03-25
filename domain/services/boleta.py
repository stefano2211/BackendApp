from typing import List, Optional
from persistencia.models import Alumno
from domain.schemas.boleta import BoletaCreate, BoletaUpdate, BoletaResponse, BoletaListResponse
from domain.schemas.calificacion import CalificacionResponse, CalificacionUpdate
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

    def contar_boletas(self) -> int:
        return self.repository.count()

    def crear_boleta(self, boleta_in: BoletaCreate) -> BoletaResponse:
        try:
            # 1. Obtener Configuración y Alumno
            config = self.config_repo.get_config()
            alumno = self.alumno_repo.get_by_id(boleta_in.alumno_id)
            
            if not alumno:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail=f"El Alumno no fue encontrado en la base de datos (ID inválido)")
                
            # Convertir a dicc para manipulacion interna (campos calculados)
            data = boleta_in.model_dump()

            # 2. Llenar campos faltantes desde Configuración y Alumno
            self._populate_from_config_and_alumno(data, config, alumno)
            
            # 3. Fallback final para evitar IntegrityError
            self._ensure_required_fields(data)
            
            print(f"DEBUG: Valores finales para crear boleta - grado: {data['grado']}, seccion: '{data['seccion']}', anio_escolar: '{data['anio_escolar']}'")

            # 5. Buscar las calificaciones existentes para este alumno y año
            calificaciones_db = self.calif_repo.get_all_by_alumno_year(
                data["alumno_id"], data["anio_escolar"]
            )
            
            # Filtrar calificaciones según modalidad de la boleta
            boleta_mod = data.get("modalidad", "Media General")
            calificaciones_db = [c for c in calificaciones_db if c.materia and c.materia.modalidad in [boleta_mod, "Ambas", "Todas"]]
            
            # 6. Calcular automatismos individuales (definitivas, etc)
            self._calcular_automatismos_db(data, calificaciones_db)
            
            # 7. NUEVO: Calcular Medias de la Sección (General y por Materia)
            medias_materia = self._calcular_medias_seccion_por_materia(
                data["grado"], data["seccion"], data.get("modalidad", "Media General"), data["anio_escolar"], data.get("hasta_lapso") or 3
            )
            
            # El promedio global de la sección es el promedio de todas las medias por materia
            if medias_materia:
                data["media_seccion"] = round(sum(medias_materia.values()) / len(medias_materia), 2)
            else:
                data["media_seccion"] = 0.0

            # 8. Guardar la boleta pasándole el diccionario completo
            db_boleta = self.repository.create(data)
            
            # 9. Re-fetch con joins
            db_boleta = self.repository.get_by_id(db_boleta.id)
            
            # Mapear respuesta incluyendo las calificaciones encontradas
            response = BoletaResponse.model_validate(db_boleta)
            
            calificaciones_response = []
            for c in calificaciones_db:
                c_res = CalificacionResponse.model_validate(c)
                # Inyectar media de sección específica
                media_seccion_val = medias_materia.get(c.materia_id, 0.0)
                c_res.media_seccion = media_seccion_val
                print(f"DEBUG: Materia {c.materia_id} - media_seccion: {media_seccion_val}")
                calificaciones_response.append(c_res)
            
            # Asignar media de sección global a la boleta
            if medias_materia:
                media_global = round(sum(medias_materia.values()) / len(medias_materia), 2)
                print(f"DEBUG: Calculando media global - sum: {sum(medias_materia.values())}, count: {len(medias_materia)}, media: {media_global}")
                response.media_seccion = media_global
            else:
                print(f"DEBUG: medias_materia está vacío, asignando 0")
                response.media_seccion = 0.0
            
            print(f"DEBUG: Boleta media_seccion final: {response.media_seccion}")
            response.calificaciones = calificaciones_response
            return response
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR IN crear_boleta: {e}")
            traceback.print_exc()
            raise e

    def _populate_from_config_and_alumno(self, data: dict, config, alumno):
        if config:
            if not data.get("anio_escolar"): data["anio_escolar"] = config.anio_escolar_actual
            if not data.get("nombre_plantel"): data["nombre_plantel"] = config.nombre_plantel
            if not data.get("direccion_plantel"): data["direccion_plantel"] = config.direccion_plantel
            if not data.get("profesor"): data["profesor"] = config.profesor_guia_default
            
        if alumno:
            if data.get("grado") is None: data["grado"] = alumno.grado if alumno.grado else 1
            if data.get("seccion") is None: data["seccion"] = alumno.seccion if alumno.seccion else "A"
            if data.get("numero_lista") is None: data["numero_lista"] = alumno.numero_lista
            if data.get("modalidad") is None: data["modalidad"] = getattr(alumno, "modalidad", "Media General")
            
            # ACTUALIZAR ALUMNO si tiene valores None
            needs_update = False
            if alumno.grado is None and data.get("grado") is not None:
                alumno.grado = data["grado"]
                needs_update = True
            if alumno.seccion is None and data.get("seccion") is not None:
                alumno.seccion = data["seccion"]
                needs_update = True
                
            if needs_update:
                self.alumno_repo.session.commit()
                print(f"DEBUG: Alumno {alumno.id} actualizado - grado: {alumno.grado}, seccion: '{alumno.seccion}'")

    def _ensure_required_fields(self, data: dict):
        if data.get("grado") is None: data["grado"] = 1
        if data.get("seccion") is None: data["seccion"] = "A"
        if not data.get("anio_escolar"): data["anio_escolar"] = "2024-2025"
        if not data.get("tipo_evaluacion"): data["tipo_evaluacion"] = "Final de Lapso"

    def _calcular_automatismos_db(self, data: dict, calificaciones: List):
        if not calificaciones:
            return

        # Tipado explícito para evitar lints
        sum_l1: float = 0.0
        count_l1: int = 0
        sum_l2: float = 0.0
        count_l2: int = 0
        sum_l3: float = 0.0
        count_l3: int = 0
        
        total_def_final: float = 0.0
        materias_numericas_count: int = 0

        # El hasta_lapso viene en el dict (o default 3)
        hasta_lapso = data.get("hasta_lapso", 3)

        for calif in calificaciones:
            materia = calif.materia
            es_numerica = materia.es_numerica if materia else True
            if not es_numerica:
                continue

            # Promedios acumulativos segun el limite solicitado (hasta_lapso)
            if hasta_lapso >= 1 and calif.lapso_1_def is not None:
                sum_l1 += float(calif.lapso_1_def)
                count_l1 += 1
            if hasta_lapso >= 2 and calif.lapso_2_def is not None:
                sum_l2 += float(calif.lapso_2_def)
                count_l2 += 1
            if hasta_lapso >= 3 and calif.lapso_3_def is not None:
                sum_l3 += float(calif.lapso_3_def)
                count_l3 += 1
                
            # Siempre sumar al promedio global (corresponde al acumulado actual)
            if calif.def_final is not None:
                total_def_final += float(calif.def_final)
                materias_numericas_count += 1

        # Asignar medias al diccionario
        if count_l1 > 0: data["media_lapso_1"] = round(sum_l1 / count_l1, 2)
        if count_l2 > 0: data["media_lapso_2"] = round(sum_l2 / count_l2, 2)
        if count_l3 > 0: data["media_lapso_3"] = round(sum_l3 / count_l3, 2)
        
        if materias_numericas_count > 0:
            data["medias_globales"] = round(total_def_final / materias_numericas_count, 2)

    def _calcular_medias_seccion_por_materia(self, grado: int, seccion: str, modalidad: str, anio: str, hasta_lapso: int) -> dict:
        """Calcula el promedio de la sección materia por materia filtrando por modalidad (OPTIMIZADO)."""
        print(f"DEBUG OPTIMIZADO: _calcular_medias_seccion_por_materia llamado con grado={grado}, seccion={seccion}, modalidad={modalidad}, anio={anio}, hasta_lapso={hasta_lapso}")
        
        # 1. Obtener TODAS las calificaciones de la sección en una sola consulta
        calificaciones_seccion = self.calif_repo.get_all_by_section_and_year(grado, seccion, anio)
        
        print(f"DEBUG: Calificaciones encontradas en sección {grado}-{seccion}: {len(calificaciones_seccion)}")
        if not calificaciones_seccion: 
            return {}
        
        # 2. Mapa de sumas por materia {materia_id: [notas]}
        mapa_notas = {}
        
        for c in calificaciones_seccion:
            # Filtrar por modalidad del alumno si es necesario (ya viene filtrado por calif_repo.materia.modalidad en teoría, 
            # pero mejor asegurar si la boleta pide una modalidad específica)
            if not c.materia or not c.materia.es_numerica:
                continue
                
            # Filtrar modalidad
            if modalidad and c.materia.modalidad not in [modalidad, "Ambas", "Todas"]:
                continue
                    
            # Determinamos que nota usar segun hasta_lapso
            nota = None
            if hasta_lapso == 1: nota = c.lapso_1_def
            elif hasta_lapso == 2: nota = c.lapso_2_def
            else: nota = c.def_final # Lapso 3 o Final
            
            if nota is not None:
                if c.materia_id not in mapa_notas: mapa_notas[c.materia_id] = []
                mapa_notas[c.materia_id].append(nota)
        
        # 3. Calcular promedios
        resultados = {m_id: round(sum(notas) / len(notas), 2) for m_id, notas in mapa_notas.items() if notas}
        
        print(f"DEBUG: _calcular_medias_seccion_por_materia (OPTIMIZADO) - resultados: {resultados}")
        return resultados

    def obtener_boleta(self, boleta_id: int) -> Optional[BoletaResponse]:
        db_boleta = self.repository.get_by_id(boleta_id)
        if not db_boleta: return None
        
        response = BoletaResponse.model_validate(db_boleta)
        
        # ACTUALIZAR ALUMNO si tiene valores None (usando datos de la boleta)
        alumno = self.alumno_repo.get_by_id(db_boleta.alumno_id)
        if alumno:
            needs_update = False
            if alumno.grado is None and db_boleta.grado is not None:
                alumno.grado = db_boleta.grado
                needs_update = True
            if alumno.seccion is None and db_boleta.seccion is not None:
                alumno.seccion = db_boleta.seccion
                needs_update = True
                
            if needs_update:
                self.alumno_repo.session.commit()
                print(f"DEBUG obtener_boleta: Alumno {alumno.id} actualizado - grado: {alumno.grado}, seccion: '{alumno.seccion}'")
        
        califs_db = self.calif_repo.get_all_by_alumno_year(
            db_boleta.alumno_id, db_boleta.anio_escolar
        )
        
        # Filtrar calificaciones según modalidad de la boleta
        boleta_mod = db_boleta.modalidad or "Media General"
        califs_db = [c for c in califs_db if c.materia and c.materia.modalidad in [boleta_mod, "Ambas", "Todas"]]
        
        # Calcular medias por materia para inyectar en la respuesta
        medias_materia = self._calcular_medias_seccion_por_materia(
            db_boleta.grado, db_boleta.seccion, db_boleta.modalidad or "Media General", db_boleta.anio_escolar, db_boleta.hasta_lapso or 3
        )
        
        calificaciones_response = []
        for c in califs_db:
            c_res = CalificacionResponse.model_validate(c)
            # Inyectar media de sección específica de esta materia
            media_seccion_val = medias_materia.get(c.materia_id, 0.0)
            c_res.media_seccion = media_seccion_val
            print(f"DEBUG obtener_boleta: Materia {c.materia_id} - media_seccion: {media_seccion_val}")
            calificaciones_response.append(c_res)
            
        # Asignar media de sección global a la boleta
        response.media_seccion = round(sum(medias_materia.values()) / len(medias_materia), 2) if medias_materia else 0.0
        print(f"DEBUG obtener_boleta: Boleta media_seccion: {response.media_seccion}")
        response.calificaciones = calificaciones_response
        return response

    def listar_boletas(self, skip: int = 0, limit: int = 100, **kwargs) -> List[BoletaListResponse]:
        db_boletas = self.repository.get_all(skip=skip, limit=limit, **kwargs)
        return [BoletaListResponse.model_validate(b) for b in db_boletas]

    def actualizar_boleta(self, boleta_id: int, boleta_in: BoletaUpdate) -> Optional[BoletaResponse]:
        db_boleta = self.repository.update(boleta_id, boleta_in)
        if db_boleta:
            return self.obtener_boleta(db_boleta.id)
        return None

    def eliminar_boleta(self, boleta_id: int) -> bool:
        # 1. Obtener la boleta para verificar existencia
        boleta = self.repository.get_by_id(boleta_id)
        if not boleta:
            return False
            
        print(f"DEBUG: Eliminando boleta {boleta_id} para alumno {boleta.alumno_id}. Las calificaciones se mantienen en la base de datos.")
        
        # 2. Solo eliminamos el registro de la boleta, nunca las notas del alumno.
        return self.repository.delete(boleta_id)
