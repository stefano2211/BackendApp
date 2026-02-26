from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from api.routers import notas

# Crear tablas en la base de datos (Nota)
# Nota: En producción sería mejor usar Alembic para migraciones
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

# Incluir routers
app.include_router(notas.router, prefix="/notas", tags=["notas"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.project_name}"}
