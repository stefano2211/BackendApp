from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from persistencia.models import Nota
from domain.schemas import NotaCreate, NotaUpdate

class NotaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, nota_in: NotaCreate) -> Nota:
        db_nota = Nota(
            titulo=nota_in.titulo,
            contenido=nota_in.contenido,
            completada=nota_in.completada
        )
        self.session.add(db_nota)
        self.session.commit()
        self.session.refresh(db_nota)
        return db_nota

    def get_by_id(self, nota_id: int) -> Optional[Nota]:
        stmt = select(Nota).where(Nota.id == nota_id)
        return self.session.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Nota]:
        stmt = select(Nota).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, nota_id: int, nota_in: NotaUpdate) -> Optional[Nota]:
        db_nota = self.get_by_id(nota_id)
        if not db_nota:
            return None
        
        update_data = nota_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_nota, key, value)

        self.session.commit()
        self.session.refresh(db_nota)
        return db_nota

    def delete(self, nota_id: int) -> bool:
        db_nota = self.get_by_id(nota_id)
        if not db_nota:
            return False
            
        self.session.delete(db_nota)
        self.session.commit()
        return True
