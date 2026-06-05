# Módulo de Búsqueda Web

El **Módulo de Búsqueda Web** complementa la recuperación local cuando los resultados del corpus indexado son insuficientes. Se activa automáticamente al detectar que la cantidad o calidad de los documentos locales no alcanza para satisfacer la consulta del usuario. Obtiene noticias frescas desde fuentes externas (Google News RSS), las procesa (descarga, extrae contenido, chunkifica) y las integra en la lista de resultados, además de indexarlas de forma asíncrona para futuras consultas.

## Arquitectura y componentes principales

El módulo sigue una **arquitectura limpia** con separación en capas:

- **Capa de dominio**: Define los contratos abstractos.
  - `WebSearchRepository`: declara la operación `search(query, max_results)`.
  - `InsufficientResultsDetector`: interfaz para evaluar si los resultados locales son insuficientes.

- **Capa de infraestructura**: Implementa los contratos con tecnologías concretas.
  - `GoogleNewsRSSFetcher`: implementa `WebSearchRepository` usando el feed RSS de Google News..
  - `SimpleInsufficientResultsDetector`: implementación concreta de `InsufficientResultsDetector`.

- **Capa de aplicación**: Alberga los casos de uso que orquestan la lógica del módulo.
  - `WebSearch`: servicio principal que orquesta el flujo completo de búsqueda web.

La **inyección de dependencias** se gestiona mediante el contenedor `WebSearchContainer` construido con la librería **`dependency-injector`**, que registra y resuelve las dependencias del módulo.

## Google News RSS como fuente externa

La fuente principal de noticias externas es el feed RSS de Google News (`https://news.google.com/rss`). El `GoogleNewsRSSFetcher` construye la URL de la consulta con los parámetros de idioma y país configurados (por defecto `es-419` y `US`).  La ejecución se realiza en un `ThreadPool` para no bloquear el event loop.

## Procesamiento de una noticia web

Para cada resultado devuelto por el RSS, el sistema realiza los siguientes pasos:

1. **Decodificación de la URL de Google News**: las URLs de Google News suelen ser redirecciones. Se utiliza `googlenewsdecoder` para obtener la URL real del artículo.

2. **Scraping del artículo**: mediante `ScrapingService` (que internamente usa el mismo sistema de adquisición de datos: `Fetcher` + scrapers especializados). Se obtiene título, contenido, autores y fecha.

3. **Chunking**: el artículo completo se divide en fragmentos (chunks) usando `ChunkingService`. Cada chunk se convierte en un `HybridSearchResult` con `source_type=WEB`.

4. **Persistencia**: Los chunks web se indexan en segundo plano (asíncrono) en ChromaDB y Elasticsearch para que estén disponibles en futuras búsquedas.

## Detector de insuficiencia (InsufficientResultsDetector)

El detector de insuficiencia evalúa si los resultados locales son suficientes para responder a la consulta sin necesidad de activar la búsqueda web. La implementación concreta `SimpleInsufficientResultsDetector` utiliza dos criterios: **cantidad** y **calidad** de los resultados.

### Clasificación de un resultado como relevante

Un resultado (`HybridSearchResult`) se considera **relevante** (y por tanto contará para la suficiencia) según las siguientes reglas:

- **Resultado híbrido** (aparece tanto en la búsqueda dispersa como en la densa): se acepta automáticamente. La coincidencia en ambas vías es una señal fuerte de relevancia.
- **Resultado puramente denso** (solo en la búsqueda semántica): se acepta si su `dense_score` (distancia coseno) es menor o igual a un umbral `max_dense_distance` (por defecto 0.6). Valores bajos indican alta similitud semántica.
- **Resultado puramente disperso** (solo en la búsqueda léxica): se acepta siempre. Se asume que el modelo LMIR ya ha realizado un filtrado implícito al devolver únicamente los candidatos mejor puntuados.

Esta lógica está implementada en el método `is_good_result` (denominado así internamente, aunque conceptualmente clasifica la relevancia). El método `filter_good_results` devuelve la lista de resultados que cumplen la condición.

### Decisión de insuficiencia

Una vez contados los resultados relevantes (`good_local_count`), el detector decide si son suficientes comparando con el número deseado `k` (documentos solicitados). La función `is_local_insufficient` aplica la siguiente lógica:

- Si `good_local_count >= k`: se considera **suficiente** → retorna `(False, 0)`.
- En caso contrario, se calcula el número de documentos que faltan: `needed = k - good_local_count`.
- A ese número se le suma un margen `extra` (por defecto 5) para solicitar más resultados web de los estrictamente necesarios, compensando posibles fallos en el scraping o en la deduplicación.
- Se retorna `(True, needed)`.

Esta estrategia garantiza que la búsqueda web solo se active cuando realmente no se alcanza la cantidad requerida de resultados locales de calidad, y pide un pequeño excedente para cubrir contingencias.

## Limitaciones y consideraciones
- Dependencia de Google News RSS: la disponibilidad de resultados está sujeta a los términos de servicio.

- Latencia: la búsqueda web añade tiempo de respuesta (descarga y scraping). Por ello se limita a unos pocos documentos y se ejecuta en paralelo dentro de lo posible.
