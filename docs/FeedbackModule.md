# Módulo de Feedback y Refinamiento

El módulo de feedback permite a los usuarios calificar la relevancia de los fragmentos (chunks) devueltos por el sistema mediante un sistema de “manita arriba” (👍) o “manita abajo” (👎). Además, incorpora un mecanismo de refinamiento de consultas que, a partir de un fragmento que recibió feedback positivo, extrae palabras clave y expande la consulta original para lanzar una nueva búsqueda, mejorando así los resultados en la sesión actual. Este módulo forma parte del componente opcional de *expansión y retroalimentación* del proyecto.

## Arquitectura y flujo

### 🧠 Panorama general

`FeedbackModule` es el módulo responsable de almacenar las valoraciones de los usuarios sobre los fragmentos recuperados y de ofrecer una operación de refinamiento basada en expansión de consultas. Está diseñado con capas claras (Domain + Infrastructure + Application + API) y utiliza el modelo de embeddings `SentenceTransformer` junto con KeyBERT para extraer términos relevantes.

El flujo principal es:

1. El usuario envía un feedback (positivo o negativo) asociado a un fragmento (`chunk_id`).
2. El sistema guarda el feedback en un repositorio (por defecto en memoria, pero puede ser persistente).
3. Si el usuario solicita “mejorar búsqueda” a partir de un fragmento con like, se extraen keywords del contenido del fragmento mediante KeyBERT.
4. Se construye una nueva consulta añadiendo esas keywords a la consulta original.
5. Se ejecuta la nueva consulta contra el motor de búsqueda híbrida y se devuelven los nuevos resultados.

## 🧩 Componentes (capas) de FeedbackModule

### 1) Domain (lógica + entidades)

- **`Feedback`** (`FeedbackModule/domain/entities.py`):
  - Entidad que representa una calificación.
  - Campos: `query`, `chunk_id`, `chunk_content`, `rating` (True = 👍, False = 👎), `user_id`, `timestamp`.

- **`RefinementResult`** (`FeedbackModule/domain/entities.py`):
  - DTO con el resultado de una operación de refinamiento.
  - Campos: `original_query`, `expanded_query`, (opcional `results`).

### 2) Infrastructure (repositorios)

- **`MemoryFeedbackRepository`** (`FeedbackModule/infrastructure/memory_feedback_repository.py`):
  - Implementación volátil (almacenamiento en memoria) de la interfaz del repositorio.
  - Métodos: `save`, `get_by_query_and_chunk`, `get_all`.

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
    - `refine_search(...)`: devuelve un `RefinementResult`.

### 4) API (routers y schemas)

- **Router** (`src/API/routers/feedback.py`):
  - Endpoint `POST /feedback/` → guarda feedback.
  - Endpoint `POST /feedback/refine` → refina búsqueda a partir de un fragmento con like.

- **Schemas** (`src/API/schemas/feedback.py`):
  - `FeedbackRequest`: `query`, `chunk_id`, `chunk_content`, `rating`, `user_id`.
  - `RefineRequest`: `original_query`, `chunk_content`, `top_n_terms`.
  - `RefineResponse`: `original_query`, `expanded_query` (y opcionalmente `results`).

## 🔍 Reglas importantes y detalles de implementación

- **Extracción de keywords**:
  - Se limpia el texto: minúsculas, eliminación de puntuación.
  - Se trunca a 1000 caracteres por eficiencia.
  - KeyBERT extrae palabras individuales (`ngram_range=(1,1)`) con stopwords en inglés.
  - Se filtran palabras de menos de 3 caracteres y duplicados.

- **Expansión de consulta**:
  - Solo se añaden keywords que **no** estén ya en la consulta original.
  - La nueva consulta es: `original_query + " " + " ".join(nuevas_keywords)`.
  - El número de términos añadidos se controla con `top_n_terms`.

- **Singleton para `RefinementService`**:
  - `SentenceTransformer` y KeyBERT son pesados; se cargan una sola vez al iniciar la aplicación y se reutilizan en todas las peticiones.

- **Repositorio volátil por defecto**:
  - `MemoryFeedbackRepository` pierde datos al reiniciar el servidor. Para persistencia real, se debe implementar `SQLiteFeedbackRepository` respetando la misma interfaz.