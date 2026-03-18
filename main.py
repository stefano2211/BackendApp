from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from api.routers import alumnos, materias, boletas, auth, calificaciones, tareas, configuracion, dashboard
from api.deps import get_current_user
from fastapi import Depends

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Protected routers require global authentication
app.include_router(alumnos.router, prefix="/alumnos", tags=["alumnos"], dependencies=[Depends(get_current_user)])
app.include_router(materias.router, prefix="/materias", tags=["materias"], dependencies=[Depends(get_current_user)])
app.include_router(calificaciones.router, prefix="/calificaciones", tags=["calificaciones"], dependencies=[Depends(get_current_user)])
app.include_router(boletas.router, prefix="/boletas", tags=["boletas"], dependencies=[Depends(get_current_user)])
app.include_router(configuracion.router, prefix="/configuracion", tags=["configuracion"], dependencies=[Depends(get_current_user)])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.project_name}"}
