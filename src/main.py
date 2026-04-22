# main.py (en la raíz del proyecto)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa los routers
from src.API.routers import search

app = FastAPI(
    title="News Retrieval System API",
    description="Sistema de recuperación de noticias con búsqueda dispersa (LMIR), densa (embeddings) e híbrida (RRF)",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema de recuperación de noticias", "docs": "/docs"}