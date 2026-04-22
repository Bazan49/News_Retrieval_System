from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any

from src.API.dependencies import get_sparse_service, get_hybrid_service, get_dense_service

router = APIRouter(prefix="/search", tags=["search"])

def _standardize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte un resultado (de sparse, dense o hybrid) a un formato común."""
    # Para dense: item puede venir con 'id', 'title', 'url', 'source', 'date', 'score', 'snippet'
    # Para sparse/hybrid: tienen 'url', 'title', 'content', 'score', 'source', 'snippet'
    return {
        "id": item.get("id") or item.get("url", ""),
        "title": item.get("title", "Sin título"),
        "url": item.get("url") or item.get("id", ""),
        "source": item.get("source", ""),
        "date": item.get("date", ""),
        "score": item.get("score", 0.0),
        "snippet": item.get("snippet", "")
    }

def _format_dense_results(raw: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """Convierte la salida cruda de VectorSearcher a lista de ítems estandarizables."""
    formatted = []
    ids = raw.get("ids", [])
    docs = raw.get("documents", [])
    distances = raw.get("distances", [])
    metadatas = raw.get("metadatas", [])
    for idx in range(len(ids)):
        item = {
            "id": ids[idx],
            "title": metadatas[idx].get("title", "Sin título") if idx < len(metadatas) else "",
            "url": ids[idx],
            "source": metadatas[idx].get("source", "") if idx < len(metadatas) else "",
            "date": metadatas[idx].get("date", "") if idx < len(metadatas) else "",
            "score": 1 - (distances[idx] / 2) if idx < len(distances) else 0,
            "snippet": docs[idx][:200] + "..." if idx < len(docs) else ""
        }
        formatted.append(item)
    return formatted

@router.get("/sparse")
async def sparse_search(
    q: str = Query(...),
    k: int = Query(10),
    service = Depends(get_sparse_service)
):
    raw_results = await service.retrieve(q, k=k)
    # Los resultados de sparse ya tienen la forma correcta, solo estandarizamos
    results = [_standardize_item(item) for item in raw_results]
    return {"query": q, "results": results}

@router.get("/dense")
async def dense_search(
    q: str = Query(...),
    k: int = Query(10),
    service = Depends(get_dense_service)
):
    raw = await service.search(q, k=k)
    items = _format_dense_results(raw)
    results = [_standardize_item(item) for item in items]
    return {"query": q, "results": results}

@router.get("/hybrid")
async def hybrid_search(
    q: str = Query(...),
    k: int = Query(10),
    service = Depends(get_hybrid_service)
):
    raw_results = await service.hybrid_search(q, k=k)
    results = [_standardize_item(item) for item in raw_results]
    return {"query": q, "results": results}