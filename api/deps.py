from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import SessionLocal

from persistencia.repositories.tarea import TareaRepository
from persistencia.repositories.alumno import AlumnoRepository
from persistencia.repositories.materia import MateriaRepository
from persistencia.repositories.calificacion import CalificacionRepository
from persistencia.repositories.boleta import BoletaRepository
from persistencia.repositories.configuracion import ConfiguracionRepository

from domain.services.tarea import TareaService
from domain.services.alumno import AlumnoService
from domain.services.materia import MateriaService
from domain.services.calificacion import CalificacionService
from domain.services.boleta import BoletaService
from domain.services.pdf import PDFService
from domain.services.configuracion import ConfiguracionService


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security import decode_access_token
from persistencia.models import User
from persistencia.repositories.user import UserRepository
from fastapi import HTTPException, status

security = HTTPBearer()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
        
    repo = UserRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


# --- PDF Service ---
def get_pdf_service() -> PDFService:
    return PDFService()


# --- Tareas (Ex-Notas) ---
def get_tarea_repository(db: Session = Depends(get_db)) -> TareaRepository:
    return TareaRepository(db)

def get_tarea_service(repository: TareaRepository = Depends(get_tarea_repository)) -> TareaService:
    return TareaService(repository)


# --- Alumnos ---
def get_alumno_repository(db: Session = Depends(get_db)) -> AlumnoRepository:
    return AlumnoRepository(db)

def get_alumno_service(repository: AlumnoRepository = Depends(get_alumno_repository)) -> AlumnoService:
    return AlumnoService(repository)


# --- Materias ---
def get_materia_repository(db: Session = Depends(get_db)) -> MateriaRepository:
    return MateriaRepository(db)

def get_materia_service(repository: MateriaRepository = Depends(get_materia_repository)) -> MateriaService:
    return MateriaService(repository)


# --- Configuracion ---
def get_configuracion_repository(db: Session = Depends(get_db)) -> ConfiguracionRepository:
    return ConfiguracionRepository(db)

def get_configuracion_service(repository: ConfiguracionRepository = Depends(get_configuracion_repository)) -> ConfiguracionService:
    return ConfiguracionService(repository)


# --- Calificaciones ---
def get_calificacion_repository(db: Session = Depends(get_db)) -> CalificacionRepository:
    return CalificacionRepository(db)

def get_calificacion_service(
    repository: CalificacionRepository = Depends(get_calificacion_repository),
    config_repo: ConfiguracionRepository = Depends(get_configuracion_repository)
) -> CalificacionService:
    return CalificacionService(repository, config_repo)


# --- Boletas ---
def get_boleta_repository(db: Session = Depends(get_db)) -> BoletaRepository:
    return BoletaRepository(db)

def get_boleta_service(
    repository: BoletaRepository = Depends(get_boleta_repository),
    calif_repo: CalificacionRepository = Depends(get_calificacion_repository),
    config_repo: ConfiguracionRepository = Depends(get_configuracion_repository),
    alumno_repo: AlumnoRepository = Depends(get_alumno_repository)
) -> BoletaService:
    return BoletaService(repository, calif_repo, config_repo, alumno_repo)
