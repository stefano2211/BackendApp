from typing import Optional
from domain.schemas.configuracion import ConfiguracionUpdate, ConfiguracionResponse
from persistencia.repositories.configuracion import ConfiguracionRepository


class ConfiguracionService:
    def __init__(self, repository: ConfiguracionRepository):
        self.repository = repository

    def obtener_config(self) -> ConfiguracionResponse:
        db_config = self.repository.get_config()
        if not db_config:
            # Si no existe, creamos uno con valores por defecto vacíos para que el repo maneje el insert al actualizar
            # O simplemente retornamos un objeto base para el cliente
            return ConfiguracionResponse(
                id=0,
                updated_at="2024-01-01T00:00:00" if False else None # Placeholder
            ).model_validate({"id": 0, "updated_at": "2024-01-01T00:00:00"}) 
        
        return ConfiguracionResponse.model_validate(db_config)

    def actualizar_config(self, config_in: ConfiguracionUpdate) -> ConfiguracionResponse:
        db_config = self.repository.update_config(config_in)
        return ConfiguracionResponse.model_validate(db_config)
