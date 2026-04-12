#!/usr/bin/env python3
"""
SCRIPT COMPLETO DE PRUEBA DEL SISTEMA SRI

Este script permite probar todo el flujo del sistema de recuperación de información:
1. Indexación de documentos de ejemplo
2. Búsqueda local (RetrievalModule)
3. Activación automática de búsqueda web (WebSearchModule)
4. Resultados combinados

Uso:
    python test_full_system.py

Opciones:
    --index-only: Solo indexar documentos
    --query "tu consulta": Hacer una consulta específica
    --no-web: Desactivar búsqueda web
    --verbose: Mostrar más detalles
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Configurar path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from DI.continer import SearchContainer
from DataAcquisitionModule.Domain.Entities.scrapedDocument import ScrapedDocument


class SRITester:
    """Clase para probar el sistema SRI completo."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.container = None
        self.index_service = None
        self.retrieval_service = None
        self.web_search_service = None

    async def setup(self):
        """Configura el contenedor y servicios."""
        print("🚀 Configurando sistema SRI...")
        print("=" * 60)

        try:
            # Inicializar contenedor
            self.container = SearchContainer()
            self.container.wire(modules=[__name__])

            # Obtener servicios
            self.index_service = self.container.index_service()
            self.retrieval_service = self.container.retrieval_service()
            self.web_search_service = self.container.web_search_service()

            print("✅ Servicios inicializados correctamente")
            if self.verbose:
                print("   - IndexService: OK")
                print("   - RetrievalService: OK")
                print("   - WebSearchService: OK")

        except Exception as e:
            print(f"❌ Error inicializando servicios: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

        return True

    def get_sample_documents(self) -> List[ScrapedDocument]:
        """Retorna documentos de ejemplo para indexar."""
        return [
            # Economía
            ScrapedDocument(
                source="cubadebate",
                url="https://cubadebate.cu/economia/2024/01",
                url_normalized="https://cubadebate.cu/economia/2024/01",
                title="La economía cubana muestra signos de recuperación",
                content="La economía cubana está mostrando signos de recuperación tras un período difícil. Los sectores turístico y agrícola han liderado el crecimiento. El gobierno ha implementado nuevas políticas para estimular la inversión extranjera y mejorar la producción nacional.",
                authors=["María García"],
                date=datetime(2024, 1, 15)
            ),
            ScrapedDocument(
                source="cubadebate",
                url="https://cubadebate.cu/economia/2024/02",
                url_normalized="https://cubadebate.cu/economia/2024/02",
                title="Sector turístico cubano supera expectativas",
                content="El sector turístico de Cuba ha superado las expectativas de crecimiento este año. Los hoteles reportan una ocupación promedio del 85%. Los expertos prevén que el turismo seguirá siendo el motor de la economía nacional.",
                authors=["Carlos López"],
                date=datetime(2024, 1, 20)
            ),
            ScrapedDocument(
                source="cubadebate",
                url="https://cubadebate.cu/economia/2024/03",
                url_normalized="https://cubadebate.cu/economia/2024/03",
                title="Inversiones extranjeras en Cuba aumentan",
                content="Las inversiones extranjeras en Cuba han aumentado significativamente en los últimos meses. Empresas de España, México y Canadá han mostrado interés en el mercado cubano. Los sectores más atractivos son el turismo y la energía renovable.",
                authors=["Ana Martínez"],
                date=datetime(2024, 2, 5)
            ),

            # Política
            ScrapedDocument(
                source="cubadebate",
                url="https://cubadebate.cu/politica/2024/01",
                url_normalized="https://cubadebate.cu/politica/2024/01",
                title="Gobierno anuncia nuevas políticas públicas",
                content="El gobierno ha anunciado nuevas políticas públicas para mejorar la educación y la salud. Se invertirá en escuelas y hospitales en todo el país. Las autoridades aseguran que estas medidas beneficiarán a la población.",
                authors=["Juan Pérez"],
                date=datetime(2024, 1, 18)
            ),
            ScrapedDocument(
                source="cubadebate",
                url="https://cubadebate.cu/politica/2024/02",
                url_normalized="https://cubadebate.cu/politica/2024/02",
                title="Elecciones municipales serán en 2024",
                content="Las elecciones municipales se celebrarán en el mes de octubre de 2024. Los ciudadanos podrán elegir a sus representantes locales. El proceso electoral será supervisado por organismos internacionales.",
                authors=["Carmen Torres"],
                date=datetime(2024, 2, 1)
            ),

            # Tecnología
            ScrapedDocument(
                source="bbc",
                url="https://bbc.com/tecnologia/2024/01",
                url_normalized="https://bbc.com/tecnologia/2024/01",
                title="Inteligencia artificial revoluciona la medicina",
                content="La inteligencia artificial está revolucionando el campo de la medicina. Nuevos algoritmos pueden detectar enfermedades con mayor precisión. Los investigadores están desarrollando sistemas de diagnóstico asistido por IA.",
                authors=["Dr. Roberto Silva"],
                date=datetime(2024, 1, 25)
            ),

            # Ciencia
            ScrapedDocument(
                source="bbc",
                url="https://bbc.com/ciencia/2024/01",
                url_normalized="https://bbc.com/ciencia/2024/01",
                title="Descubrimiento científico en física cuántica",
                content="Científicos han hecho un importante descubrimiento en el campo de la física cuántica. El experimento demuestra nuevas propiedades de las partículas subatómicas. Este avance podría revolucionar la computación cuántica.",
                authors=["Dra. Elena Vargas"],
                date=datetime(2024, 2, 10)
            )
        ]

    async def index_sample_documents(self):
        """Indexa documentos de ejemplo."""
        print("\n📥 Indexando documentos de ejemplo...")
        print("-" * 60)

        try:
            documents = self.get_sample_documents()
            print(f"📄 Documentos a indexar: {len(documents)}")

            if self.verbose:
                for i, doc in enumerate(documents, 1):
                    print(f"   {i}. {doc.title[:50]}...")

            # Indexar documentos
            await self.index_service.index_scraped_documents(documents)

            print("✅ Documentos indexados correctamente")
            print(f"   Total: {len(documents)} documentos")

        except Exception as e:
            print(f"❌ Error indexando documentos: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

        return True

    async def test_query(self, query: str, enable_web_search: bool = True):
        """Ejecuta una consulta completa."""
        print(f"\n🔍 Probando consulta: '{query}'")
        print("-" * 60)

        try:
            # Paso 1: Recuperación local
            print("📍 Paso 1: Recuperación local...")
            local_results = await self.retrieval_service.retrieve(query, k=10)
            print(f"   Resultados locales: {len(local_results)}")

            if self.verbose and local_results:
                for i, result in enumerate(local_results[:3], 1):
                    print(f"     {i}. {result.get('title', 'Sin título')[:40]}... (score: {result.get('score', 0):.2f})")

            # Paso 2: Búsqueda con fallback web (si está habilitada)
            if enable_web_search:
                print("\n🌐 Paso 2: Búsqueda con fallback web...")
                result = await self.web_search_service.search_with_fallback(
                    query=query,
                    local_results=local_results,
                    web_results_limit=5,
                    insufficiency_threshold=0.5,
                    store_web_results=True
                )

                # Mostrar resultados
                print("📊 RESULTADOS FINALES:")
                print(f"   Locales: {len(result['local_results'])}")
                print(f"   Web: {len(result['web_results'])}")
                print(f"   Total combinado: {result['total_results']}")
                print(f"   Web search activada: {result['web_search_triggered']}")
                print(f"   Score insuficiencia: {result['insufficiency_score']:.2f}")

                # Mostrar algunos resultados
                print("\n📄 RESULTADOS COMBINADOS:")
                for i, res in enumerate(result['combined_results'][:5], 1):
                    source = res.get('source', 'Desconocida')
                    title = res.get('title', 'Sin título')[:50]
                    score = res.get('score', 0)
                    print(f"   {i}. [{source}] {title}... (score: {score:.2f})")

                return result
            else:
                print("\n📊 RESULTADOS LOCALES:")
                print(f"   Total: {len(local_results)}")
                for i, res in enumerate(local_results[:5], 1):
                    title = res.get('title', 'Sin título')[:50]
                    score = res.get('score', 0)
                    print(f"   {i}. {title}... (score: {score:.2f})")

                return {"local_results": local_results, "web_results": [], "combined_results": local_results}

        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return None

    async def run_comprehensive_test(self, enable_web_search: bool = True):
        """Ejecuta pruebas comprensivas con diferentes tipos de queries."""
        print("\n🧪 EJECUTANDO PRUEBAS COMPRENSIVAS")
        print("=" * 60)

        test_queries = [
            # Queries que deberían encontrar resultados locales
            ("economía cubana", "Query con resultados locales (economía)"),
            ("política gobierno", "Query con resultados locales (política)"),
            ("inteligencia artificial medicina", "Query con resultados locales (tecnología)"),

            # Queries que podrían activar web search
            ("noticias recientes cambio climático", "Query que podría necesitar web search"),
            ("últimas noticias tecnología blockchain", "Query de actualidad"),
            ("crisis diplomática internacional", "Query de eventos actuales"),
        ]

        results_summary = []

        for query, description in test_queries:
            print(f"\n🎯 {description}")
            print(f"Query: '{query}'")

            result = await self.test_query(query, enable_web_search)
            if result:
                summary = {
                    "query": query,
                    "description": description,
                    "local_count": len(result.get('local_results', [])),
                    "web_count": len(result.get('web_results', [])),
                    "total_count": result.get('total_results', 0),
                    "web_triggered": result.get('web_search_triggered', False),
                    "insufficiency_score": result.get('insufficiency_score', 0)
                }
                results_summary.append(summary)

        # Mostrar resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)

        total_web_activations = sum(1 for r in results_summary if r['web_triggered'])
        avg_insufficiency = sum(r['insufficiency_score'] for r in results_summary) / len(results_summary)

        print(f"Total de queries probadas: {len(results_summary)}")
        print(f"Web search activada: {total_web_activations} veces")
        print(f"Tasa de activación: {total_web_activations/len(results_summary):.1%}")
        print(f"Score insuficiencia promedio: {avg_insufficiency:.2f}")

        print("\nDetalle por query:")
        for r in results_summary:
            status = "🌐 WEB" if r['web_triggered'] else "📍 LOCAL"
            print(f"  {status} '{r['query'][:30]}...' → {r['total_count']} resultados")

    async def run_interactive_mode(self):
        """Modo interactivo para hacer queries manuales."""
        print("\n🎮 MODO INTERACTIVO")
        print("=" * 60)
        print("Escribe 'exit' para salir")
        print("Escribe 'help' para ver comandos")
        print()

        while True:
            try:
                query = input("🔍 Query: ").strip()

                if query.lower() in ['exit', 'quit', 'q']:
                    print("👋 ¡Hasta luego!")
                    break
                elif query.lower() in ['help', 'h', '?']:
                    print("\nComandos disponibles:")
                    print("  help    - Mostrar esta ayuda")
                    print("  exit    - Salir del modo interactivo")
                    print("  <query> - Hacer una búsqueda")
                    print()
                    continue
                elif not query:
                    continue

                await self.test_query(query, enable_web_search=True)
                print()

            except KeyboardInterrupt:
                print("\n👋 Interrumpido por usuario")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()


async def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Prueba completa del sistema SRI")
    parser.add_argument("--index-only", action="store_true", help="Solo indexar documentos")
    parser.add_argument("--query", type=str, help="Hacer una consulta específica")
    parser.add_argument("--no-web", action="store_true", help="Desactivar búsqueda web")
    parser.add_argument("--comprehensive", action="store_true", help="Ejecutar pruebas comprensivas")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar más detalles")

    args = parser.parse_args()

    # Inicializar tester
    tester = SRITester(verbose=args.verbose)

    # Configurar sistema
    if not await tester.setup():
        return 1

    # Indexar documentos
    if not await tester.index_sample_documents():
        return 1

    # Modo index-only
    if args.index_only:
        print("\n✅ Indexación completada. Saliendo...")
        return 0

    # Query específica
    if args.query:
        await tester.test_query(args.query, enable_web_search=not args.no_web)
        return 0

    # Pruebas comprensivas
    if args.comprehensive:
        await tester.run_comprehensive_test(enable_web_search=not args.no_web)
        return 0

    # Modo interactivo (default)
    if args.interactive or not any([args.index_only, args.query, args.comprehensive]):
        await tester.run_interactive_mode()
        return 0

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        if "--verbose" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)
