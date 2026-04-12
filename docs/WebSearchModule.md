# WebSearchModule - Módulo de Búsqueda Web

## Descripción General

El WebSearchModule implementa un sistema de búsqueda web que se activa automáticamente cuando los resultados del índice local son insuficientes para responder a una consulta del usuario. Utiliza Google News RSS como fuente de datos y se integra completamente con el pipeline de recuperación de información.

## Arquitectura

### Componentes Principales

#### 1. **Domain Layer**

##### `WebSearchResult`

Entidad que representa un resultado de búsqueda web obtenido de RSS.

```python
@dataclass
class WebSearchResult:
    title: str          # Título del artículo
    link: str          # URL del artículo
    published: datetime # Fecha de publicación
    summary: str       # Resumen del artículo
    source: str        # Fuente RSS
```

##### `WebSearchRepository` (Interface)

Define el contrato para obtener resultados de búsqueda web.

```python
async def search(query: str, max_results: int = 10) -> List[WebSearchResult]
```

##### `InsufficientResultsDetector` (Interface)

Determina si los resultados locales son insuficientes para activar búsqueda web.

```python
async def is_insufficient(query: str, retrieved_results: List[Dict], threshold: float) -> bool
async def get_insufficiency_score(query: str, retrieved_results: List[Dict]) -> float
```

#### 2. **Infrastructure Layer**

##### `GoogleNewsRSSFetcher`

Implementación de `WebSearchRepository` que usa feedparser para obtener noticias de Google News RSS.

- **Características:**
  - Búsqueda asincrónica (no bloquea el event loop)
  - Manejo de múltiples idiomas (es-419 por defecto)
  - Parseo automático de fechas
  - Manejo robusto de errores

```python
fetcher = GoogleNewsRSSFetcher(lang="es-419", country="US")
results = await fetcher.search("crisis política", max_results=10)
```

##### `SimpleInsufficientResultsDetector`

Implementación de `InsufficientResultsDetector` basada en criterios simples pero efectivos.

**Criterios de Insuficiencia:**

1. Número mínimo de resultados (default: 3)
2. Puntuación promedio mínima (default: -50.0)
3. Sin resultados locales = máxima insuficiencia

**Score = (60% cantidad) + (40% calidad)**

```python
detector = SimpleInsufficientResultsDetector(
    min_results=3,
    min_score_threshold=-50.0,
    empty_results_insufficient=True
)
score = await detector.get_insufficiency_score(query, results)
is_insufficient = await detector.is_insufficient(query, results, threshold=0.5)
```

##### `WebSearchDocumentProcessor`

Convierte `WebSearchResult` en `SearchDocument` para indexación.

```python
processor = WebSearchDocumentProcessor()
search_doc = processor.process_web_result(web_result)
search_docs = processor.process_batch(web_results)
```

#### 3. **Application Layer**

##### `WebSearchService`

Servicio principal que orquesta la búsqueda web integrada con recuperación.

**Responsabilidades:**

- Detectar insuficiencia de resultados locales
- Ejecutar búsqueda web como complemento
- Procesar e indexar resultados web
- Combinar resultados evitando duplicados

**Método Principal:**

```python
result = await web_search_service.search_with_fallback(
    query="política Venezuela",
    local_results=local_search_results,
    web_results_limit=5,
    insufficiency_threshold=0.5,
    store_web_results=True
)

# Retorna:
{
    "local_results": [...],           # Resultados del índice
    "web_results": [...],             # Resultados webSearch
    "combined_results": [...],        # Combinados y ordenados
    "web_search_triggered": bool,     # Si se activó búsqueda web
    "insufficiency_score": float,     # Score 0-1
    "total_results": int              # Total de resultados
}
```

## Flujo de Integración

### Caso 1: Resultados Suficientes

```
Usuario Query
    ↓
Recuperación Local → Suficientes → Devolver Resultados
    ↓
No activa web search
```

### Caso 2: Resultados Insuficientes

```
Usuario Query
    ↓
Recuperación Local → Insuficientes → Detector activado
    ↓
Google News RSS → Obtener artículos
    ↓
Procesar → Convertir a SearchDocument
    ↓
Indexar → Almacenar en ElasticSearch
    ↓
Combinar resultados + Evitar duplicados
    ↓
Devolver Resultados (Local + Web)
```

## Uso Práctica

### Integración con RetrievalModule

```python
from WebSearchModule.Application.web_search_service import WebSearchService
from DI.continer import SearchContainer

# Inicializar container
container = SearchContainer()
web_search_service = container.web_search_service()
retrieval_service = container.retrieval_service()

# Búsqueda
query = "últimas noticias economía"
local_results = await retrieval_service.retrieve(query, k=10)

# Búsqueda con fallback automático
result = await web_search_service.search_with_fallback(
    query=query,
    local_results=local_results,
    web_results_limit=10,
    insufficiency_threshold=0.5
)

print(f"Total resultados: {result['total_results']}")
print(f"Web search activada: {result['web_search_triggered']}")
```

### Solo Búsqueda Web

```python
web_results = await web_search_service.web_search_repo.search(
    "crisis diplomática",
    max_results=15
)

for result in web_results:
    print(f"{result.title}")
    print(f"  {result.link}")
    print(f"  {result.published}")
```

### Detectar Insuficiencia

```python
detector = web_search_service.insufficiency_detector

# Evaluar resultados específicos
score = await detector.get_insufficiency_score(query, local_results)
if score > 0.5:
    print("Resultados insuficientes, activar búsqueda web")
```

## Configuración

### En el Container

```python
# DI/continer.py
insufficiency_detector = providers.Singleton(
    SimpleInsufficientResultsDetector,
    min_results=3,           # Mínimo de resultados
    min_score_threshold=-50.0,  # Puntuación mínima
    empty_results_insufficient=True
)

web_search_fetcher = providers.Singleton(
    GoogleNewsRSSFetcher,
    lang="es-419",    # Idioma
    country="US"      # País
)
```

### Parámetros de `search_with_fallback`

| Parámetro                 | Tipo  | Default | Descripción                   |
| ------------------------- | ----- | ------- | ----------------------------- |
| `query`                   | str   | -       | Consulta del usuario          |
| `local_results`           | List  | -       | Resultados del índice local   |
| `web_results_limit`       | int   | 5       | Máximo de resultados web      |
| `insufficiency_threshold` | float | 0.5     | Umbral (0-1) para activar web |
| `store_web_results`       | bool  | True    | Indexar resultados web        |

## Ejemplos de Casos de Uso

### Caso 1: Noticias de Actualidad

```
Query: "últimas noticias"
→ Índice local: Documentos históricos
→ Detector: Score 0.8 (muy insuficiente)
→ Activar: Google News RSS
→ Resultado: Noticias recientes + históricos
```

### Caso 2: Tema Cubierto Localmente

```
Query: "constitución política"
→ Índice local: 15 documentos relevantes, score -20
→ Detector: Score 0.0 (suficiente)
→ Activar: No
→ Resultado: Solo resultados locales
```

### Caso 3: Tema Parcialmente Cubierto

```
Query: "inflación Venezuela"
→ Índice local: 1-2 documentos, score -60
→ Detector: Score 0.6 (insuficiente)
→ Activar: Google News RSS
→ Almacenar: Nuevos artículos indexados
```

## Extensiones Posibles

### 1. Múltiples Fuentes RSS

```python
class MultiSourceWebSearchRepository(WebSearchRepository):
    async def search(self, query: str, max_results: int) -> List[WebSearchResult]:
        # Buscar en múltiples feeds
```

### 2. Detector Avanzado

```python
class MLInsufficientResultsDetector(InsufficientResultsDetector):
    # Usar ML para evaluar insuficiencia
```

### 3. Caché de Resultados

```python
class CachedWebSearchRepository(WebSearchRepository):
    # Cachear resultados para queries recientes
```

### 4. Ranking Inteligente

```python
def _combine_results_intelligent(self, local, web):
    # Usar algorithms para mejor ranking
```

## Consideraciones Importantes

### Rendimiento

- La búsqueda web es asincrónica (no bloquea)
- Se ejecuta bajo demanda (cuando es necesario)
- Los resultados se indexan para reutilización

### Privacidad

- Google News RSS es público
- No se almacenan datos personales
- Respeta términos de servicio de Google

### Exactitud

- Los resultados RSS dependen de Google News
- Se combina con resultados locales para mayor confiabilidad
- Los criterios de insuficiencia pueden ajustarse

