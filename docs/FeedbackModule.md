# Módulo de Feedback y Refinamiento

El módulo de feedback permite a los usuarios calificar la relevancia de los fragmentos (chunks) devueltos por el sistema mediante un sistema de “manita arriba” (👍) o “manita abajo” (👎). Además, incorpora un mecanismo de **refinamiento de consultas** que, a partir de un fragmento que recibió feedback positivo, extrae palabras clave y expande la consulta original para lanzar una nueva búsqueda, mejorando así los resultados en la sesión actual. Este módulo forma parte del componente opcional de *expansión y retroalimentación* del proyecto.

---

## Arquitectura y flujo

### 🧠 Panorama general

`FeedbackModule` es el módulo responsable de:

- Almacenar de forma **persistente** las valoraciones de los usuarios sobre los fragmentos recuperados (usando SQLite).
- Ofrecer una operación de **refinamiento** basada en expansión de consultas (KeyBERT + SentenceTransformer).
- Proveer datos de feedback que serán utilizados por el **módulo de recomendación** para construir el perfil de usuario y personalizar resultados.

El flujo principal es:

1. El usuario envía un feedback (positivo o negativo) asociado a un fragmento (`chunk_id`) mediante `POST /feedback/`.
2. El sistema guarda el feedback en una base de datos SQLite (`feedback.db`) con índices para consultas rápidas.
3. Si el usuario solicita “mejorar búsqueda” (`POST /feedback/refine`) sobre un fragmento que recibió like, se extraen keywords del fragmento, se expande la consulta original y se ejecuta una nueva búsqueda híbrida, devolviendo los resultados actualizados.

Los feedbacks almacenados son consumidos por `UserProfileBuilder` (del módulo de recomendación) para construir el perfil del usuario y personalizar futuras búsquedas a través de `PersonalizedRankingStrategy`.

---

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
  - Métodos principales:
    - `save(feedback)`: guarda un feedback.
    - `get_by_user_id(user_id, limit)`: obtiene feedbacks de un usuario (usado por el módulo de recomendación).
    - `get_all_positive(limit)`, `get_all_negative(limit)`, `get_all(limit)`: accesos generales.

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
    - `refine_search(...)`: llama a `search_service.hybrid_search()` con la consulta expandida y devuelve `RefinementResult`.

### 4) API (routers y schemas)

- **Router** (`src/API/routers/feedback.py`):
  - `POST /feedback/` → guarda feedback.
  - `POST /feedback/refine` → refina búsqueda a partir de un fragmento con like (devuelve resultados reales).

- **Schemas** (`src/API/schemas/feedback.py`):
  - `FeedbackRequest`: `query`, `chunk_id`, `chunk_content`, `rating`, `user_id`.
  - `RefineRequest`: `original_query`, `chunk_content`, `top_n_terms`.
  - `RefineResponse`: `original_query`, `expanded_query`, `results` (lista de `HybridSearchResultSchema`).

### 5) Inyección de dependencias

- **Contenedor de feedback** (`src/DI/feedback_container.py`):
  - Registra `Settings` (configuración del modelo y `top_n`).
  - Registra `SQLiteFeedbackRepository` como singleton (ruta `feedback.db`).
  - Registra `FeedbackService` (factory).
  - Registra `RefinementService` como singleton (para cargar el modelo una sola vez).

- **Exposición en `dependencies.py`**:
  - `get_feedback_service()` → `FeedbackService`.
  - `get_refinement_service()` → `RefinementService`.

---

## 🔍 Reglas importantes y detalles de implementación

### Persistencia

- **Base de datos SQLite**: archivo `feedback.db` en la raíz del proyecto. Se crea automáticamente al primer guardado.
- **Índices**: `idx_query`, `idx_user`, `idx_rating` aceleran las consultas.

### Refinamiento de consulta (expansión explícita)

- El endpoint `/refine` recibe `original_query`, `chunk_content` y `top_n_terms`.
- `RefinementService.expand_query()` extrae keywords (KeyBERT) del `chunk_content` y las añade a la consulta original si no están ya presentes.
- Luego llama a `search_service.hybrid_search()` con la consulta expandida y devuelve los nuevos resultados (10 por defecto).
- **Nota:** Este refinamiento es **explícito** (solo se activa cuando el usuario lo pide).

### Uso de feedbacks por otros módulos

- El módulo de **recomendación** (`UserProfileBuilder`) utiliza `SQLiteFeedbackRepository.get_by_user_id()` para obtener los likes/dislikes de un usuario y construir su perfil de intereses.

### Configuración

| Variable / Parámetro | Valor por defecto | Descripción |
|----------------------|-------------------|-------------|
| `refinement_model_name` | `all-MiniLM-L6-v2` | Modelo de `SentenceTransformer` para extracción de keywords |
| `refinement_top_n` | 5 | Número máximo de términos a añadir en expansión |

Los valores se definen en `Settings` (archivo `.env`).

---

## Ventajas

- **Persistencia**: Los feedbacks sobreviven a reinicios del servidor gracias a SQLite.
- **Refinamiento explícito**: El usuario puede refinar su consulta basándose en un fragmento que le gustó, obteniendo resultados más precisos.
- **Modularidad**: El módulo proporciona datos de feedback que son reutilizados por el módulo de recomendación sin acoplamiento directo.

## Limitaciones actuales

- **Sin re‑ranking automático**: El feedback no influye automáticamente en los resultados de búsqueda (la personalización se delega al módulo de recomendación).
- **Dependencia de la calidad de KeyBERT**: La extracción de keywords puede no ser perfecta para textos muy cortos o técnicos.