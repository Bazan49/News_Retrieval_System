from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer

from pathlib import Path

# Configuración de logging
from src.logging_config import setup_logging
setup_logging()

# Importar los routers
from src.API.routers import feedback
from src.API.routers import web_search
from src.API.routers import search
from src.API.routers import rag
from src.API.routers import hybrid_search
from src.API.routers import recommendation
from src.API.routers import auth
from src.API.middleware.timing_middleware import TimingMiddleware

app = FastAPI(
    title="News Retrieval System API",
    description="Sistema de recuperación de noticias.",
    version="1.0.0"
)

# Crear directorio para bases de datos SQLite si no existe
DB_FOLDER = "sqlite_data"
Path(DB_FOLDER).mkdir(exist_ok=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

app.add_middleware(TimingMiddleware)

# Configurar CORS (permite peticiones desde cualquier origen durante desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(search.router)
app.include_router(rag.router)
app.include_router(hybrid_search.router)
app.include_router(web_search.router)
app.include_router(feedback.router) 
app.include_router(recommendation.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema de recuperación de noticias", "docs": "/docs"}