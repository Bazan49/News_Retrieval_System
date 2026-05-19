from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar los routers
from src.API.routers import search
from src.API.routers import rag
from src.API.routers import hybrid_search

app = FastAPI(
    title="News Retrieval System API",
    description="Sistema de recuperación de noticias.",
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
app.include_router(rag.router)
app.include_router(hybrid_search.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido al sistema de recuperación de noticias", "docs": "/docs"}