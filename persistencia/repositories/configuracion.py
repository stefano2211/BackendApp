from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from persistencia.models import Configuracion
from domain.schemas.configuracion import ConfiguracionUpdate


class ConfiguracionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_config(self) -> Optional[Configuracion]:
        stmt = select(Configuracion).limit(1)
        return self.session.scalars(stmt).first()

    def update_config(self, config_in: ConfiguracionUpdate) -> Configuracion:
        db_config = self.get_config()
        
        if not db_config:
            db_config = Configuracion(**config_in.model_dump())
            self.session.add(db_config)
        else:
            update_data = config_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_config, key, value)
        
        self.session.commit()
        self.session.refresh(db_config)
        return db_config
