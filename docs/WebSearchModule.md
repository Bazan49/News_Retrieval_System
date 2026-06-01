# WebSearchModule – Módulo de Búsqueda Web con Fallback Automático

El módulo de búsqueda web proporciona un mecanismo de **fallback automático** cuando los resultados del índice local (búsqueda híbrida) son insuficientes para responder a una consulta. Se integra directamente con el pipeline de recuperación, permitiendo obtener noticias frescas desde Google News RSS, procesarlas e indexarlas para futuras consultas.

## Arquitectura y componentes principales

Siguiendo los principios de **Arquitectura Limpia**, el módulo se organiza en las siguientes capas:

### 🔹 Capa de dominio

- **`WebSearchResult`** : entidad que representa un resultado de búsqueda web (título, enlace, fecha, resumen, fuente).
- **`WebSearchRepository`** : interfaz abstracta para la obtención de resultados web (contrato que deben implementar las infraestructuras).
- **`InsufficientResultsDetector`** : interfaz para evaluar si los resultados locales son insuficientes (debe implementarse con una lógica concreta).

### 🔹 Capa de infraestructura

- **`GoogleNewsRSSFetcher`** : implementación de `WebSearchRepository` que consulta el feed RSS de Google News de forma asíncrona (usa `feedparser` y `asyncio.to_thread`).
- **`SimpleInsufficientResultsDetector`** : detector concreto que analiza la cantidad, calidad y contenido mínimo de los resultados locales. Proporciona métodos como `filter_good_results` y `is_local_insufficient`.
- **`WebSearchDocumentProcessor`** : convierte `WebSearchResult` en `SearchDocument` (para indexación) y genera IDs cortos a partir de la URL.

### 🔹 Capa de aplicación

- **`WebSearch`** : caso de uso que, a partir de una consulta, obtiene resultados web, limpia las URLs de Google News, realiza scraping del contenido y genera trozos (`Chunk`) y resultados híbridos (`HybridSearchResult`) listos para ser combinados con resultados locales.
- **`WebFallbackHybridSearchService`** : servicio orquestador principal que coordina:
  - Búsqueda híbrida local (a través de `FusionService`).
  - Filtrado de resultados “buenos” usando el detector.
  - Activación de la búsqueda web si los resultados locales son insuficientes.
  - Almacenamiento asíncrono de los trozos web (indexación en el sistema de chunks).
  - Fusión final de resultados (web + locales) evitando duplicados por URL.

La **inyección de dependencias** se realiza mediante un contenedor (`WebSearchContainer`) que registra las dependencias necesarias (repositorio RSS, detector, procesador, etc.) y las proporciona al orquestador.

## Flujo completo de búsqueda con fallback web

El siguiente diagrama representa el flujo que sigue una consulta cuando se utiliza `WebFallbackHybridSearchService`:
```text
Consulta del usuario
↓
┌──────────────────────────────────────────┐
│ Búsqueda híbrida local (FusionService)   │
└──────────────────────────────────────────┘
↓
┌──────────────────────────────────────────┐
│ Filtrar resultados "buenos" usando       │
│ SimpleInsufficientResultsDetector        │
│(rrf_score > threshold y contenido mínimo)│
└──────────────────────────────────────────┘
↓
┌──────────────────────────────────────────┐
│ ¿Cantidad de resultados buenos ≥ k?      │
└──────────────────────────────────────────┘
│
No │ Sí
↓   ↓
┌──────────────────┐     ┌──────────────────┐
│ Activar fallback │     │ Devolver         │
│ web              │     │ resultados       │
└──────────────────┘     │ locales          │
                         └──────────────────┘
↓
┌──────────────────────────────────────────┐
│ WebSearch.fetch_web_results()            │
│ - Obtener resultados RSS                 │
│ - Limpiar URLs de Google News            │
│ - Scraping del contenido                 │
│ - Generar Chunk                          │
│ - Crear HybridSearchResult               │
└──────────────────────────────────────────┘
↓
┌──────────────────────────────────────────┐
│ Almacenar los Chunks en el sistema       │
│ (ChunkPersistenceService)                │
│ (se ejecuta en segundo plano)            │
└──────────────────────────────────────────┘
↓
┌──────────────────────────────────────────┐
│ Fusionar resultados: web + locales       │
│ (se priorizan los web)                   │
└──────────────────────────────────────────┘
↓
┌──────────────────────────────────────────┐
│ Devolver top‑k resultados combinados     │
└──────────────────────────────────────────┘
```

## Componentes clave en detalle

### 1. `WebFallbackHybridSearchService`

Orquesta todo el flujo. Recibe en su constructor:

- `fusion_service` (búsqueda híbrida local)
- `web_search` (caso de uso de búsqueda web)
- `chunk_persistence` (para indexar los nuevos trozos)
- `insufficiency_detector` (para evaluar calidad y necesidad de fallback)
- `settings` (configuración: umbrales, etc.)

**Método principal**:

```python
async def search(query: str, k: int = 10, user_id: Optional[str] = None) -> List[HybridSearchResult]
```
## 2. WebSearch (caso de uso)

Se encarga de la obtención y procesamiento completo de resultados web. Utiliza el repositorio RSS, un servicio de scraping y un servicio de chunking. Devuelve una tupla `(lista_de_HybridSearchResult, lista_de_Chunk)`.

### `fetch_web_results(query, max_results)`

- Obtiene los RSS items.
- Para cada uno:
  - Limpia la URL de Google News (usa `googlenewsdecoder`).
  - Realiza scraping del contenido completo.
  - Divide el documento en trozos (`Chunk`).
  - Convierte cada trozo en un `HybridSearchResult` (con `source_type=ResultSource.WEB` y `rrf_score=0.0`).
- Retorna todos los `HybridSearchResult` y `Chunk` generados.

## 3. `SimpleInsufficientResultsDetector`

Implementa la lógica para decidir si los resultados locales son suficientes. Además de los métodos de la interfaz (`is_insufficient`, `get_insufficiency_score`), proporciona:

- `filter_good_results(results)` : devuelve solo aquellos resultados que superan el umbral `good_rrf_threshold`, tienen contenido mínimo y título no vacío.
- `is_local_insufficient(good_local_count, k, extra=5)` : calcula si hacen falta resultados web (si `good_local_count < k`) y cuántos se necesitan (agregando un margen extra).

Los umbrales (`good_rrf_threshold`, `min_content_length`) se obtienen de las `settings` o se pasan directamente.

## 4. `GoogleNewsRSSFetcher`

Implementación concreta de `WebSearchRepository`. Parámetros de configuración:

- `lang`: código de idioma (por defecto `es-419`).
- `country`: código de país (por defecto `US`).

Construye la URL de Google News RSS con los parámetros y parsea el feed usando `feedparser`. La ejecución se realiza en un `ThreadPool` para no bloquear el event loop (`asyncio.to_thread`).

## 5. `WebSearchDocumentProcessor`

Utilizado principalmente para **indexar** los resultados web (almacenarlos en el sistema de búsqueda). Convierte un `WebSearchResult` en un `SearchDocument` (con campos `source`, `url`, `title`, `content`, `authors` nulos y `date`). También genera un ID corto (`web_<hash16>`) para cada documento.

## Integración con el pipeline principal

El módulo de búsqueda web no se utiliza de forma aislada, sino como parte del servicio de búsqueda híbrida extendido. En el contenedor de dependencias (`WebSearchContainer`) se registran:

- `google_news_rss_fetcher` (con idioma y país)
- `insufficiency_detector` (con umbrales ajustables)
- `web_search_document_processor`
- `web_search` (caso de uso)
- `web_fallback_hybrid_search_service` (orquestador)

El orquestador se inyecta en los endpoints de la API (por ejemplo, `/hybrid/web`) y sustituye a la búsqueda híbrida local cuando se desea el fallback automático.

