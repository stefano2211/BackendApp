from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import SessionLocal

from persistencia.repositories.nota import NotaRepository
from persistencia.repositories.alumno import AlumnoRepository
from persistencia.repositories.materia import MateriaRepository
from persistencia.repositories.boleta import BoletaRepository

from domain.services.nota import NotaService
from domain.services.alumno import AlumnoService
from domain.services.materia import MateriaService
from domain.services.boleta import BoletaService
from domain.services.pdf import PDFService


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwe, jwt
from core.security import SECRET_KEY, ALGORITHM, decode_access_token
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


# --- Notas ---
def get_nota_repository(db: Session = Depends(get_db)) -> NotaRepository:
    return NotaRepository(db)

def get_nota_service(repository: NotaRepository = Depends(get_nota_repository)) -> NotaService:
    return NotaService(repository)


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


# --- Boletas ---
def get_boleta_repository(db: Session = Depends(get_db)) -> BoletaRepository:
    return BoletaRepository(db)

def get_boleta_service(repository: BoletaRepository = Depends(get_boleta_repository)) -> BoletaService:
    return BoletaService(repository)
