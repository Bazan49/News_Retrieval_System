# Módulo de Feedback y Refinamiento

El módulo de feedback permite a los usuarios calificar la relevancia de los fragmentos (chunks) devueltos por el sistema mediante un sistema de “manita arriba” (👍) o “manita abajo” (👎). Además, incorpora un mecanismo de **refinamiento de consultas** que, a partir de un fragmento que recibió feedback positivo, extrae palabras clave y expande la consulta original para lanzar una nueva búsqueda, mejorando así los resultados en la sesión actual. También se implementa un **re‑ranking automático** que, en cada búsqueda, ajusta la relevancia de los documentos según el feedback histórico (likes/dislikes) y la actualidad de la publicación (frescura). Este módulo forma parte del componente opcional de *expansión y retroalimentación* del proyecto.

## Arquitectura y flujo

### 🧠 Panorama general

`FeedbackModule` es el módulo responsable de:

- Almacenar de forma **persistente** las valoraciones de los usuarios sobre los fragmentos recuperados (usando SQLite).
- Ofrecer una operación de **refinamiento** basada en expansión de consultas (KeyBERT + SentenceTransformer).
- Proporcionar una **estrategia de re‑ranking** (`FeedbackRankingStrategy`) que se inyecta en el `FusionService` y modifica los scores finales (`final_score`) combinando:
  - El score original RRF.
  - Ajustes por feedback (boost para likes, penalización para dislikes).
  - Un factor de **frescura** (decaimiento exponencial según la fecha de publicación).

El flujo principal es:

1. El usuario envía un feedback (positivo o negativo) asociado a un fragmento (`chunk_id`).
2. El sistema guarda el feedback en una base de datos SQLite (`feedback.db`) con índices para consultas rápidas.
3. En cada búsqueda híbrida, el `FusionService` obtiene los resultados RRF y luego llama a `FeedbackRankingStrategy.rerank_with_query()`.
4. La estrategia:
   - Recupera feedbacks positivos y negativos para consultas similares (usando `LIKE` parcial).
   - Aplica boost o penalización sobre `rrf_score`.
   - Aplica un boost de frescura basado en `published_date`.
   - Asigna el nuevo `final_score` y reordena los resultados.
5. Si el usuario solicita “mejorar búsqueda”  sobre un fragmento que recibió like, se extraen keywords del fragmento, se expande la consulta original y se ejecuta una nueva búsqueda híbrida, devolviendo los resultados actualizados.

## 🧩 Componentes (capas) de FeedbackModule

### 1) Domain (lógica + entidades)

- **`Feedback`** (`FeedbackModule/domain/entities.py`):
  - Entidad que representa una calificación.
  - Campos: `query`, `chunk_id`, `chunk_content`, `rating` (True = 👍, False = 👎), `user_id`, `timestamp`.

- **`RefinementResult`** (`FeedbackModule/domain/entities.py`):
  - DTO con el resultado de una operación de refinamiento.
  - Campos: `original_query`, `expanded_query`, `results` (lista de `HybridSearchResult`).

### 2) Infrastructure (repositorios)

- **`SQLiteFeedbackRepository`** (`FeedbackModule/infrastructure/sqlite_feedback_repository.py`):
  - Implementación persistente usando `aiosqlite`.
  - Tabla `feedback` con índices sobre `query`, `user_id` y `rating`.
  - Métodos:
    - `save(feedback)`: guarda un feedback.
    - `get_positive_by_similar_query(query, limit)`: devuelve likes para consultas que contengan la cadena de búsqueda (usando `LIKE`).
    - `get_negative_by_similar_query(query, limit)`: análogo para dislikes.
  - **Nota:** El antiguo `MemoryFeedbackRepository` se conserva pero no se usa en producción.

### 3) Application (servicios)

- **`FeedbackService`** (`FeedbackModule/application/feedback_service.py`):
  - Orquesta la creación y guardado de feedback.
  - Flujo: recibe datos, crea entidad `Feedback`, invoca `repository.save()`.

- **`RefinementService`** (`FeedbackModule/application/refinement_service.py`):
  - Servicio central para extraer palabras clave y expandir consultas.
  - Utiliza `SentenceTransformer` (modelo configurable) y `KeyBERT`.
  - Métodos principales:
    - `extract_keywords(text, top_n)`: limpia el texto y extrae las palabras clave más relevantes.
    - `expand_query(original_query, chunk_content, top_n)`: genera una nueva consulta añadiendo las keywords que no están ya en la consulta original.
    - `refine_search(...)`: llama a `search_service.hybrid_search()` con la consulta expandida y devuelve `RefinementResult` con los nuevos resultados.

### 4) Ranking y Re‑ranking

- **`FeedbackRankingStrategy`** (`RankingModule/Infrastructure/feedback_ranking_strategy.py`):
  - Implementa la interfaz `RankingStrategy`.
  - Se inyecta en `FusionService` (en `RankingContainer`).
  - Parámetros configurables: `boost_factor` (0.3), `penalty_factor` (0.5), `recency_weight` (0.5), `recency_decay_days` (30).
  - El método `rerank_with_query(query, results)`:
    1. Recupera feedbacks relevantes (usando `LIKE` en `query`).
    2. Para cada resultado, ajusta `rrf_score` con `*(1+boost)` o `*(1-penalty)`.
    3. Calcula `recency_boost` basado en `published_date` y lo multiplica.
    4. Asigna `final_score` y reordena la lista.

- **`FusionService`** (`RankingModule/Application/hybrid_search.py`):
  - Ahora acepta un `ranking_strategy` opcional.
  - Después de fusionar los resultados dispersos y densos con RRF, aplica el re‑ranking si la estrategia está presente.

### 5) API (routers y schemas)

- **Router** (`src/API/routers/feedback.py`):
  - `POST /feedback/` → guarda feedback.
  - `POST /feedback/refine` → refina búsqueda a partir de un fragmento con like (devuelve resultados reales).

- **Schemas** (`src/API/schemas/feedback.py`):
  - `FeedbackRequest`: `query`, `chunk_id`, `chunk_content`, `rating`, `user_id`.
  - `RefineRequest`: `original_query`, `chunk_content`, `top_n_terms`.
  - `RefineResponse`: `original_query`, `expanded_query`, `results` (lista de `HybridSearchResultSchema`).

### 6) Inyección de dependencias

- **Contenedor** (`src/DI/feedback_container.py`):
  - Registra `Settings` (configuración del modelo y `top_n`).
  - Registra `SQLiteFeedbackRepository` como singleton (ruta `feedback.db`).
  - Registra `FeedbackService` (factory).
  - Registra `RefinementService` como singleton (para cargar el modelo una sola vez).

- **Contenedor de ranking** (`src/DI/ranking_container.py`):
  - Registra `FeedbackRankingStrategy` inyectándole el repositorio de feedback y el servicio de refinamiento.
  - Inyecta esta estrategia en `FusionService`.

- **Exposición en `dependencies.py`**:
  - `get_feedback_service()` → devuelve `FeedbackService`.
  - `get_refinement_service()` → devuelve `RefinementService`.

## 🔍 Reglas importantes y detalles de implementación

### Persistencia y consultas

- **Base de datos SQLite**: archivo `feedback.db` en la raíz del proyecto. Se crea automáticamente al primer guardado.
- **Similitud de consultas**: se usa `LIKE '%consulta%'` para recuperar feedbacks cuya consulta original contenga términos de la búsqueda actual. Es una aproximación simple pero efectiva. No se utiliza FTS5 para evitar complejidad.
- **Índices**: `idx_query`, `idx_user`, `idx_rating` aceleran las consultas.

### Re‑ranking automático

- Se ejecuta **siempre** que `ranking_strategy` esté presente (lo está por defecto).
- El `final_score` se calcula como:
final_score = rrf_score * (1 + boost) * (1 - penalty) * recency_boost
donde `boost` es `boost_factor` (0.3) si el documento tiene algún like en consultas similares, y `penalty` es `penalty_factor` (0.5) si tiene algún dislike.
- El `recency_boost` es:
recency_boost = 1 + recency_weight * exp(-días_antigüedad / recency_decay_days)
Con `recency_weight=0.5`, un documento del día de hoy tiene boost 1.5; a los 30 días baja a ~1.18.
- Los resultados se ordenan por `final_score` descendente.

### Refinamiento de consulta

- El endpoint `/refine` recibe `original_query`, `chunk_content` y `top_n_terms`.
- `RefinementService.expand_query()` extrae keywords (KeyBERT) del `chunk_content` y las añade a la consulta original si no están ya presentes.
- Luego llama a `search_service.hybrid_search()` con la consulta expandida y devuelve los nuevos resultados (10 por defecto).
- **Nota:** Este refinamiento es **explícito** (solo se activa cuando el usuario lo pide), a diferencia del re‑ranking automático que ocurre en cada búsqueda.

### Configuración

| Variable / Parámetro | Valor por defecto | Descripción |
|----------------------|-------------------|-------------|
| `refinement_model_name` | `all-MiniLM-L6-v2` | Modelo de `SentenceTransformer` para extracción de keywords |
| `refinement_top_n` | 5 | Número máximo de términos a añadir en expansión |
| `boost_factor` | 0.3 | Incremento del score por cada like relevante |
| `penalty_factor` | 0.5 | Reducción del score por cada dislike relevante |
| `recency_weight` | 0.5 | Peso máximo del factor de frescura |
| `recency_decay_days` | 30 | Días para que la frescura decaiga a ~37% |

Los valores se definen en `Settings` (archivo `.env`) y se inyectan a través de los contenedores.

## Ventajas

- **Persistencia**: Los feedbacks sobreviven a reinicios del servidor gracias a SQLite.
- **Re‑ranking automático**: Mejora la calidad de los resultados en cada búsqueda sin intervención del usuario.
- **Frescura**: Los documentos recientes obtienen un boost, relevante para un dominio de noticias.
- **Modularidad**: La estrategia de ranking está desacoplada del resto del sistema y puede ser reemplazada o ajustada fácilmente.
- **Refinamiento explícito**: El usuario puede refinar su consulta basándose en un fragmento que le gustó, obteniendo resultados más precisos.

## Limitaciones actuales

- **Similitud de consultas básica**: El uso de `LIKE` puede ser impreciso; no se utiliza similitud semántica entre consultas (embeddings). Podría mejorarse en el futuro.
- **El re‑ranking no es personalizado por usuario**: Se aplica a todos los usuarios por igual. Podría extenderse filtrando por `user_id`.
- **El factor de frescura depende de la calidad de `published_date`**: Si la fecha no está disponible o tiene formato incorrecto, no se aplica.
