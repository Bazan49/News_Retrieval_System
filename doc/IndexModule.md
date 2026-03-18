# IndexModule - Arquitectura y flujo

## 🧠 Panorama general
`IndexModule` es el módulo responsable de **indexar documentos scraped** en ElasticSearch usando una arquitectura basada en capas (Domain + Infrastructure + Application), con inyección de dependencias para separar responsabilidades.

El flujo principal es:

1. Se obtienen `ScrapedDocument` desde el módulo de scraping.
2. Se transforman a `SearchDocument` (limpios y listos para indexar) mediante `DefaultDocumentProcessor`.
3. Se asegura que el índice existe en ElasticSearch (creación con mapping).
4. Se indexan los documentos en lote (`bulk`) y se refresca el índice.

---

## 🧩 Componentes (capas) de IndexModule

### 1) Domain (lógica + contratos)

- **`SearchDocument`** (`IndexModule/Domain/search_document.py`)
  - Representa el documento final que se guarda en ElasticSearch.
  - Campos: `source`, `url`, `title`, `content`, `authors`, `date`.

- **`DefaultDocumentProcessor`** (`IndexModule/Domain/document_processor.py`)
  - Convierte `ScrapedDocument` → `SearchDocument`.

- **`IndexRepository`** (`IndexModule/Domain/index_repository.py`)
  - Interfaz de repositorio (abstracta) usada por el servicio.
  - Define métodos async:
    - `ensure_index()`
    - `index_one(...)`, `index_bulk(...)`
    - `delete_by_id(...)`
    - `refresh()`

---

### 2) Infrastructure (implementaciones concretas para ElasticSearch)

- **`ElasticsearchClient`** (`IndexModule/Infrastructure/ElasticSearch/elasticsearch_client.py`)
  - Crea clientes `sync` y `async` de ElasticSearch.

- **`ElasticsearchIndexRepository`** (`IndexModule/Infrastructure/ElasticSearch/elasticsearch_index_repository.py`)
  - Implementa `IndexRepository` usando `AsyncElasticsearch`.
  - `ensure_index()` crea el índice si no existe, usando un archivo JSON de mapping.
  - `index_bulk()` utiliza `async_bulk` para rendimiento.

- **`mapping.json`** (`IndexModule/Infrastructure/ElasticSearch/mapping.json`)
  - Define el mapping del índice (tipos, analizadores, campos, etc.).

---

### 3) Application (orquestación del flujo)

- **`IndexService`** (`IndexModule/Application/index_service.py`)
  - Orquesta el flujo completo:
    1. `ensure_index()`
    2. Convierte docs con `DefaultDocumentProcessor`
    3. `index_bulk()`
    4. `refresh()`

- **`index_main.py`** (ejemplo)
  - Muestra cómo inicializar el contenedor, construir documentos y llamar al servicio.

---

## 🧩 Inyección de dependencias (DI)

- **`SearchContainer`** (`src/DI/continer.py`)
  - Usa `dependency_injector`.
  - Registra:
    - Cliente Elastic (`ElasticsearchClient`)
    - Repositorio (`ElasticsearchIndexRepository`)
    - Servicio (`IndexService`)

---

## 🛠 Flujo de indexación (paso a paso)

1. `ScrapedDocument` llega desde el módulo de scraping.
2. `IndexService.index_scraped_documents()` recibe la lista.
3. Llama a `ensure_index()` para garantizar el índice.
4. Se mapea cada documento a `SearchDocument`.
5. Llama a `index_bulk(...)` para indexar masivamente.
6. Llama a `refresh()` para que los documentos estén disponibles.

---

## 🧪 Cómo probar rápidamente

1. Asegúrate de que ElasticSearch esté corriendo en la URL configurada.
2. Ajusta credenciales / hosts en `.env` o `Settings`.
3. Ejecuta código similar al de `index_main.py`.

---

## 🔎 Recomendaciones

- Mantén el mapping y la configuración de ElasticSearch en un `.env` o config centralizada.
- Evita hardcodear credenciales en scripts de prueba.
- Si necesitas más repositorios (p.ej. otro motor de búsqueda), crea otra implementación de `IndexRepository`.
