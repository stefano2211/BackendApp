from fastapi import APIRouter, Depends
from domain.schemas.configuracion import ConfiguracionUpdate, ConfiguracionResponse
from domain.services.configuracion import ConfiguracionService
from api.deps import get_configuracion_service

router = APIRouter()

@router.get("/", response_model=ConfiguracionResponse)
def get_config(
    service: ConfiguracionService = Depends(get_configuracion_service)
) -> ConfiguracionResponse:
    return service.obtener_config()

@router.post("/", response_model=ConfiguracionResponse)
@router.put("/", response_model=ConfiguracionResponse)
def update_config(
    config_in: ConfiguracionUpdate,
    service: ConfiguracionService = Depends(get_configuracion_service)
) -> ConfiguracionResponse:
    return service.actualizar_config(config_in)
