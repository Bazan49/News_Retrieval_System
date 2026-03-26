#!/usr/bin/env python3
"""
Script de prueba para el módulo de embeddings.
Prueba la indexación y búsqueda de documentos.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument
from DI.embeddings_container import EmbeddingsContainer


def create_sample_documents():
    """Crea documentos de ejemplo para pruebas."""
    docs = [
        ScrapedDocument(
            source="TestSource",
            url="https://example.com/article1",
            url_normalized="example_com_article1",
            title="Título del Artículo 1",
            content="Este es el contenido del primer artículo. Habla sobre temas importantes como la inteligencia artificial, machine learning y procesamiento de lenguaje natural. Es un artículo extenso que cubre varios aspectos técnicos.",
            authors=["Autor 1"],
            date=datetime.now(),
            indexed=False,
            embeddings_generated=False
        ),
        ScrapedDocument(
            source="TestSource",
            url="https://example.com/article2",
            url_normalized="example_com_article2",
            title="Título del Artículo 2",
            content="El segundo artículo discute sobre bases de datos vectoriales y embeddings. Explica cómo funcionan los sistemas de búsqueda por similitud y las técnicas de chunking para documentos largos.",
            authors=["Autor 2"],
            date=datetime.now(),
            indexed=False,
            embeddings_generated=False
        ),
        ScrapedDocument(
            source="TestSource",
            url="https://example.com/article3",
            url_normalized="example_com_article3",
            title="Título del Artículo 3",
            content="Este artículo trata sobre el procesamiento de documentos en español y cómo los modelos multilingües pueden manejar diferentes idiomas de manera efectiva.",
            authors=["Autor 3"],
            date=datetime.now(),
            indexed=False,
            embeddings_generated=False
        )
    ]
    return docs


def main():
    print("🚀 Iniciando prueba del módulo de embeddings...")

    # Crear container
    try:
        container = EmbeddingsContainer()
        indexer = container.vector_indexer()
        searcher = container.vector_searcher()
        print("✅ Container y servicios creados exitosamente")
    except Exception as e:
        print(f"❌ Error creando container: {e}")
        return

    # Crear documentos de prueba
    documents = create_sample_documents()
    print(f"📄 Creados {len(documents)} documentos de prueba")

    # Indexar documentos
    try:
        total_chunks = indexer.index(documents)
        print(f"✅ Indexados {total_chunks} chunks exitosamente")
    except Exception as e:
        print(f"❌ Error en indexación: {e}")
        return

    # Probar búsquedas
    queries = [
        "inteligencia artificial",
        "bases de datos vectoriales",
        "procesamiento en español"
    ]

    for query in queries:
        try:
            print(f"\n🔍 Buscando: '{query}'")
            results = searcher.search(query, k=2)
            print(f"   Encontrados {len(results.get('documents', []))} resultados")

            # Mostrar resultados
            docs = results.get('documents', [])
            metadatas = results.get('metadatas', [])
            distances = results.get('distances', [])

            for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances)):
                print(f"   {i+1}. {meta.get('title', 'Sin título')} (distancia: {dist:.4f})")
                print(f"      Contenido: {doc[:100]}...")

        except Exception as e:
            print(f"❌ Error en búsqueda '{query}': {e}")

    print("\n🎉 Prueba completada!")


if __name__ == "__main__":
    main()