#!/usr/bin/env python3
"""
SCRIPT PARA VERIFICAR DOCUMENTOS INDEXADOS

Este script permite verificar qué documentos están almacenados en ElasticSearch,
especialmente los resultados de búsqueda web.

Uso:
    python check_indexed_documents.py
    python check_indexed_documents.py --source "web"
    python check_indexed_documents.py --query "economía"
    python check_indexed_documents.py --limit 10
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Configurar path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from elasticsearch import AsyncElasticsearch
from IndexModule.Config.settings import Settings


class IndexInspector:
    """Inspecciona el contenido del índice ElasticSearch."""

    def __init__(self):
        self.settings = Settings()
        self.client = AsyncElasticsearch(
            hosts=self.settings.elasticsearch_hosts,
            basic_auth=(self.settings.elasticsearch_username, self.settings.elasticsearch_password),
            verify_certs=False
        )

    async def get_index_stats(self) -> dict:
        """Obtiene estadísticas del índice."""
        try:
            stats = await self.client.indices.stats(index=self.settings.index_name)
            return {
                "total_docs": stats["indices"][self.settings.index_name]["total"]["docs"]["count"],
                "deleted_docs": stats["indices"][self.settings.index_name]["total"]["docs"]["deleted"],
                "size": stats["indices"][self.settings.index_name]["total"]["store"]["size_in_bytes"]
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {}

    async def search_documents(
        self,
        query: str = None,
        source: str = None,
        limit: int = 20,
        sort_by_date: bool = True
    ) -> list:
        """Busca documentos en el índice."""
        # Construir query
        es_query = {"match_all": {}}

        if query or source:
            must_clauses = []
            if query:
                must_clauses.append({"multi_match": {"query": query, "fields": ["title", "content"]}})
            if source:
                must_clauses.append({"term": {"source": source}})

            es_query = {"bool": {"must": must_clauses}}

        # Ordenar por fecha más reciente
        sort = [{"date": {"order": "desc"}}] if sort_by_date else None

        try:
            response = await self.client.search(
                index=self.settings.index_name,
                query=es_query,
                size=limit,
                sort=sort
            )

            documents = []
            for hit in response["hits"]["hits"]:
                doc = hit["_source"]
                doc["_id"] = hit["_id"]
                doc["_score"] = hit["_score"]
                documents.append(doc)

            return documents

        except Exception as e:
            print(f"Error buscando documentos: {e}")
            return []

    async def get_recent_web_documents(self, hours: int = 24) -> list:
        """Obtiene documentos de búsqueda web recientes."""
        since = datetime.now() - timedelta(hours=hours)

        query = {
            "bool": {
                "must": [
                    {"range": {"date": {"gte": since.isoformat()}}}
                ],
                "should": [
                    {"term": {"source": "Google News"}},
                    {"term": {"source": "web"}},
                    {"wildcard": {"source": "*news*"}}
                ],
                "minimum_should_match": 1
            }
        }

        try:
            response = await self.client.search(
                index=self.settings.index_name,
                query=query,
                size=50,
                sort=[{"date": {"order": "desc"}}]
            )

            documents = []
            for hit in response["hits"]["hits"]:
                doc = hit["_source"]
                doc["_id"] = hit["_id"]
                doc["_score"] = hit["_score"]
                documents.append(doc)

            return documents

        except Exception as e:
            print(f"Error obteniendo documentos web recientes: {e}")
            return []

    async def close(self):
        """Cierra la conexión."""
        await self.client.close()


async def main():
    parser = argparse.ArgumentParser(description="Verificar documentos indexados en ElasticSearch")
    parser.add_argument("--query", help="Buscar documentos que contengan este texto")
    parser.add_argument("--source", help="Filtrar por fuente (ej: 'web', 'Google News')")
    parser.add_argument("--limit", type=int, default=20, help="Número máximo de resultados")
    parser.add_argument("--recent-web", action="store_true", help="Mostrar solo documentos web recientes (últimas 24h)")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas del índice")

    args = parser.parse_args()

    inspector = IndexInspector()

    try:
        print("🔍 INSPECTOR DE ÍNDICE ELASTICSEARCH")
        print("=" * 50)

        # Mostrar estadísticas
        if args.stats or not any([args.query, args.source, args.recent_web]):
            print("\n📊 ESTADÍSTICAS DEL ÍNDICE:")
            stats = await inspector.get_index_stats()
            if stats:
                print(f"   Total documentos: {stats['total_docs']}")
                print(f"   Documentos eliminados: {stats['deleted_docs']}")
                print(f"   Tamaño del índice: {stats['size'] / 1024 / 1024:.2f} MB")
            else:
                print("   No se pudieron obtener estadísticas")

        # Buscar documentos web recientes
        if args.recent_web:
            print(f"\n🌐 DOCUMENTOS WEB RECIENTES (últimas 24h):")
            docs = await inspector.get_recent_web_documents()
            if docs:
                for i, doc in enumerate(docs[:args.limit], 1):
                    print(f"\n{i}. [{doc.get('source', 'N/A')}] {doc.get('title', 'Sin título')}")
                    print(f"   URL: {doc.get('url', 'N/A')}")
                    print(f"   Fecha: {doc.get('date', 'N/A')}")
                    print(f"   ID: {doc.get('_id', 'N/A')}")
                    if 'content' in doc and len(doc['content']) > 100:
                        print(f"   Contenido: {doc['content'][:100]}...")
            else:
                print("   No se encontraron documentos web recientes")

        # Búsqueda general
        elif args.query or args.source:
            print(f"\n📄 RESULTADOS DE BÚSQUEDA:")
            docs = await inspector.search_documents(
                query=args.query,
                source=args.source,
                limit=args.limit
            )

            if docs:
                for i, doc in enumerate(docs, 1):
                    print(f"\n{i}. [{doc.get('source', 'N/A')}] {doc.get('title', 'Sin título')}")
                    print(f"   URL: {doc.get('url', 'N/A')}")
                    print(f"   Fecha: {doc.get('date', 'N/A')}")
                    print(f"   Score: {doc.get('_score', 'N/A')}")
                    print(f"   ID: {doc.get('_id', 'N/A')}")
                    if 'content' in doc and len(doc['content']) > 100:
                        print(f"   Contenido: {doc['content'][:100]}...")
            else:
                print("   No se encontraron documentos")

        # Vista general
        else:
            print(f"\n📄 ÚLTIMOS {args.limit} DOCUMENTOS:")
            docs = await inspector.search_documents(limit=args.limit)
            if docs:
                for i, doc in enumerate(docs, 1):
                    print(f"\n{i}. [{doc.get('source', 'N/A')}] {doc.get('title', 'Sin título')}")
                    print(f"   Fecha: {doc.get('date', 'N/A')}")
                    print(f"   ID: {doc.get('_id', 'N/A')}")
            else:
                print("   No se encontraron documentos")

        print(f"\n✅ Inspección completada")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await inspector.close()


if __name__ == "__main__":
    asyncio.run(main())