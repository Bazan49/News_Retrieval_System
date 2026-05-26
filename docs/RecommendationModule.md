# Módulo de Recomendación (Basado en Contenido)

El módulo de recomendación permite generar sugerencias personalizadas de documentos (noticias) para un usuario, basándose en su **perfil de usuario** construido a partir de dos fuentes de información:

- **Feedback explícito**: “manita arriba” (👍) y “manita abajo” (👎) que el usuario ha dado a fragmentos de noticias.
- **Comportamiento implícito**: historial de consultas de búsqueda realizadas por el usuario.

A partir de estos datos, el sistema calcula un **vector de perfil** (promedio ponderado de embeddings de los contenidos valorados y de las consultas) y lo utiliza de dos formas:

1. **Re‑ranking personalizado en búsquedas**: Cuando un usuario realiza una búsqueda (endpoint `/hybrid/web` con `user_id`), los resultados se reordenan para priorizar documentos semánticamente cercanos a su perfil, combinando la relevancia original con la similitud al perfil.
2. **Endpoint independiente de recomendación**: Se puede consultar explícitamente el endpoint `/recommend/for-user` para obtener una lista de documentos recomendados sin necesidad de una consulta de búsqueda.

Este módulo forma parte del componente opcional de **recomendación** del proyecto.

---

## Arquitectura y flujo

### 🧠 Panorama general

`RecommendationModule` es el módulo responsable de:

- Almacenar el **historial de búsquedas** de cada usuario en una tabla SQLite (`search_history.db`).
- Construir un **perfil vectorial del usuario** combinando:
  - Embeddings de los fragmentos que el usuario ha valorado positivamente (👍) con peso positivo, y negativamente (👎) con peso negativo (por defecto +1.0 y -0.5).
  - Embeddings de las consultas recientes (por defecto las últimas 20) con un peso configurable (por defecto 0.3).
- **Personalizar los resultados de búsqueda** mediante una estrategia de re‑ranking (`PersonalizedRankingStrategy`) que se inserta en el pipeline de `FusionService` junto con la estrategia de re‑ranking por feedback (`FeedbackRankingStrategy`). Ambas se aplican secuencialmente.
- Exponer un endpoint independiente de recomendación (`/recommend/for-user`) que devuelve documentos similares al perfil.

El flujo principal de integración con la búsqueda es:

1. El usuario realiza una búsqueda híbrida (`GET /hybrid/web?q=...&user_id=...`).
2. El `FusionService` obtiene resultados híbridos (RRF) y luego aplica en orden:
   - `FeedbackRankingStrategy` (basado en feedback agregado de todos los usuarios).
   - `PersonalizedRankingStrategy` (basado en el perfil del usuario actual, si se proporcionó `user_id`).
3. La `PersonalizedRankingStrategy`:
   - Obtiene el vector de perfil del usuario mediante `UserProfileBuilder` (con caché de perfil TTL).
   - Para cada resultado, calcula la similitud coseno entre el perfil y el contenido del documento (con caché de embeddings por documento).
   - Combina el score original (`final_score` o `rrf_score`) con la similitud al perfil mediante un promedio ponderado (parámetro `personalization_weight`).
   - Reordena los resultados según el nuevo score.
4. Los resultados personalizados se devuelven al usuario.

---

## 🧩 Componentes (capas) de RecommendationModule

### 1) Domain (lógica + entidades e interfaces)

- **`UserProfile`** (`RecommendationModule/Domain/entities.py`):
  - Representa el perfil de un usuario (vector de embedding y momento de última actualización).

- **`RecommendationRequest`** (`RecommendationModule/Domain/entities.py`):
  - DTO con la solicitud: `user_id`, número máximo de resultados, qué fuentes incluir (likes, consultas) y el peso relativo de las consultas.

- **`RecommendationResult`** (`RecommendationModule/Domain/entities.py`):
  - DTO con el resultado: `user_id`, lista de documentos recomendados (`RetrievalResult`) y sus puntuaciones de similitud.

- **`SearchHistoryRepository`** (`RecommendationModule/Domain/interfaces/search_history_repository.py`):
  - Interfaz para guardar y recuperar el historial de consultas.

- **`ProfileRepository`** (`RecommendationModule/domain/Interfaces/profile_repository.py`):
  - Interfaz para obtener los feedbacks de un usuario (se implementa en `SQLiteFeedbackRepository` con `get_by_user_id`).

### 2) Infrastructure (repositorios concretos)

- **`SQLiteSearchHistoryRepository`** (`RecommendationModule/Infrastructure/sqlite_search_history_repository.py`):
  - Implementación persistente usando `aiosqlite`.
  - Tabla `search_history` con índice por `user_id`.
  - Métodos: `save_query(user_id, query)` y `get_recent_queries(user_id, limit)`.

- **`SQLiteFeedbackRepository`** (ya existente en `FeedbackModule`) se extiende con el método:
  - `get_by_user_id(user_id, limit)`: obtiene solo los feedbacks de un usuario (más eficiente).

### 3) Application (servicios)

- **`UserProfileBuilder`** (`RecommendationModule/Application/user_profile_builder.py`):
  - Construye el vector de perfil.
  - Utiliza **doble caché**:
    - `_embedding_cache`: evita recalcular embedding del mismo texto (fragmento o consulta).
    - `_profile_cache`: almacena el perfil de cada usuario con un TTL configurable (por defecto 300 segundos).
  - Parámetros configurables: `like_weight`, `dislike_weight`, `max_queries`, `profile_cache_ttl`.
  - El método `build_embedding_profile()`:
    1. Verifica si existe perfil en caché y no ha expirado.
    2. Si no, obtiene feedbacks y consultas, genera embeddings (usando caché de texto) y calcula promedio ponderado.
    3. Guarda el perfil en caché con timestamp.

- **`ContentRecommender`** (`RecommendationModule/Application/content_based_recommender.py`):
  - Servicio utilizado por el endpoint independiente `/recommend/for-user`.
  - Obtiene el vector de perfil, busca documentos similares en ChromaDB, aplica boost de frescura y devuelve recomendaciones.
  - **No se usa en el flujo de búsqueda**, solo para el endpoint separado.

### 4) Re‑ranking personalizado en búsquedas (integración con módulo recuperador)

- **`PersonalizedRankingStrategy`** (`RankingModule/Infrastructure/personalized_ranking_strategy.py`):
  - Implementa la interfaz `RankingStrategy`.
  - Se inyecta en `FusionService` como parte de la lista `ranking_strategies`.
  - Parámetros: `profile_builder` (de `RecommendationContainer`), `embedder` (de `EmbeddingsContainer`), `personalization_weight` (0.4 por defecto).
  - Utiliza **caché de embeddings de documentos** (`_doc_embedding_cache`) para evitar recalcular el embedding del mismo documento en múltiples búsquedas.
  - Método `rerank_with_user(user_id, results)`:
    1. Obtiene el perfil del usuario (desde `UserProfileBuilder`, que ya aplica su propia caché).
    2. Para cada resultado, obtiene el embedding del documento desde la caché (o lo calcula y lo guarda).
    3. Calcula similitud coseno y combina con el score original.
    4. Reordena la lista por `final_score`.

- **`FeedbackRankingStrategy`** (ya existente) se aplica **antes** de la personalización, ajustando scores por feedback agregado de todos los usuarios y frescura.

- **`FusionService`** (`RankingModule/Application/hybrid_search.py`):
  - Acepta una lista `ranking_strategies` y la recorre en orden.
  - Pasa `user_id` a las estrategias que lo requieren.

### 5) API (routers, schemas y mappers)

- **Router de búsqueda** (`src/API/routers/hybrid_search.py`):
  - Se añadió `user_id` opcional en `SearchQueryParams`.
  - Si se proporciona, la consulta se guarda en `search_history` (para construir el perfil) y se pasa al servicio de búsqueda.
  - Los resultados ya están personalizados gracias al re‑ranking.

- **Router de recomendación** (`src/API/routers/recommendation.py`):
  - `POST /recommend/for-user` (o `GET`) → devuelve recomendaciones independientes.

- **Schemas**:
  - `RecommendationRequestSchema` (`src/API/schemas/recommendation_request.py`).
  - `RecommendationResponse` (`src/API/schemas/recommendation_response.py`).

- **Mappers** (`src/API/mappers/recommendation_mapper.py`):
  - Convierten `RetrievalResult` a `SearchResultItem`.

---

## 🔍 Reglas importantes y detalles de implementación

### Persistencia y consultas optimizadas

- **Historial de búsquedas**: tabla `search_history` con índice por `user_id`.
- **Recuperación de feedbacks**: se utiliza `get_by_user_id(user_id)` para filtrar directamente en SQLite.
- **Caché de embeddings**: tres niveles:
  1. `UserProfileBuilder._embedding_cache`: para textos de feedbacks y consultas.
  2. `UserProfileBuilder._profile_cache`: para perfiles de usuario (TTL 5 minutos).
  3. `PersonalizedRankingStrategy._doc_embedding_cache`: para embeddings de documentos (vida completa de la instancia).

### Construcción del perfil de usuario

| Fuente | Peso por defecto | Nota |
|--------|------------------|------|
| Like (👍) | +1.0 | Peso positivo |
| Dislike (👎) | -0.5 | Peso negativo (penalización) |
| Consulta (búsqueda) | `query_weight` (0.3) | Peso adicional para cada consulta reciente |

- El perfil es el promedio ponderado: `profile = (Σ w_i * emb_i) / Σ w_i`.
- Si no hay datos, se devuelve `None` y el re‑ranking personalizado no modifica los resultados.

### Re‑ranking personalizado en búsquedas

- Se aplica **después** de la fusión RRF y del re‑ranking por feedback agregado.
- La combinación de scores es:  
  `final_score = original_score * (1 - personalization_weight) + profile_similarity * personalization_weight`
- `personalization_weight` controla cuánto influye el perfil (por defecto 0.4).
- El embedding del documento se obtiene de la caché (`_doc_embedding_cache`), lo que evita recálculos costosos.
- Los resultados se ordenan por `final_score` descendente.

### Endpoint independiente de recomendación

- `POST /recommend/for-user` (o `GET`) → devuelve documentos similares al perfil, excluyendo aquellos que el usuario ya ha valorado.
- Incluye boost de frescura (`recency_weight` y `recency_decay_days`).
- Se utiliza `search_by_vector` de `VectorSearcher`.

### Configuración (valores por defecto)

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `like_weight` | 1.0 | Peso de cada like |
| `dislike_weight` | -0.5 | Peso de cada dislike |
| `max_queries` | 20 | Número máximo de consultas recientes |
| `query_weight` | 0.3 | Peso de cada consulta |
| `recency_weight` | 0.2 | Peso máximo del boost de frescura (en recomendación) |
| `recency_decay_days` | 30 | Días para que el boost decaiga a ~37% |
| `personalization_weight` | 0.4 | Influencia del perfil en el re‑ranking de búsqueda |
| `profile_cache_ttl` | 300 | Tiempo de vida del perfil en caché (segundos) |
| `max_results` (recomendación) | 10 | Documentos sugeridos en el endpoint independiente |

---

## Ventajas

- **Personalización activa en búsquedas**: Los resultados de búsqueda se adaptan automáticamente al perfil del usuario sin necesidad de acciones adicionales.
- **Modularidad**: La estrategia de re‑ranking personalizado se integra limpiamente en el pipeline de ranking existente.
- **Reutilización**: El mismo `UserProfileBuilder` se usa tanto para el endpoint independiente como para el re‑ranking.
- **Alto rendimiento**: Las cachés de embeddings (textos y documentos) y de perfiles reducen drásticamente el costo computacional en búsquedas repetidas.

## Limitaciones actuales

- **Embedding de documentos bajo demanda**: Aunque hay caché, el primer cálculo por documento sigue siendo costoso. Para cargas muy altas, se recomienda precomputar y almacenar embeddings en la base de datos.
- **No se consideran otros metadatos** (categorías, autores) en la similitud, solo el contenido textual.

---
