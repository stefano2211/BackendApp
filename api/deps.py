from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import SessionLocal
from persistencia.repository import NotaRepository
from domain.services import NotaService

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_nota_repository(db: Session = Depends(get_db)) -> NotaRepository:
    return NotaRepository(db)

def get_nota_service(repository: NotaRepository = Depends(get_nota_repository)) -> NotaService:
    return NotaService(repository)
