# Sistema de Recuperación de Noticias

**News Retrieval System** es un sistema de recuperación de información y generación aumentada (RAG) diseñado para el dominio de noticias y periodismo digital. El sistema combina un modelo probabilístico de lenguaje (Language Model con suavizado Dirichlet) sobre un índice Elasticsearch con búsqueda semántica en una base de datos vectorial ChromaDB utilizando embeddings `jinaai/jina-embeddings-v2-base-es`. Un módulo de búsqueda web (Google News RSS) se activa automáticamente al detectar insuficiencia de resultados locales mediante un detector basado en cantidad y puntuación mínima. Se incorporan módulos opcionales de retroalimentación explícita (refinamiento de consultas) y recomendación basada en contenido (perfil de usuario vectorial).

### Prerrequisitos

- **Docker y Docker Compose**
- **Git**

## 🔧 Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Bazan49/News_Retrieval_System.git
cd News_Retrieval_System
```

### 2. Crear archivo `.env`

Copie el archivo de ejemplo y complete al menos las tres variables obligatorias:

```bash
cp .env.example .env
```

- `ELASTICSEARCH_PASSWORD`: elija una contraseña segura.
- `MISTRAL_API_KEY`: obtenga una clave gratuita en [console.mistral.ai](https://console.mistral.ai) (para el módulo RAG).
- `SECRET_KEY`: clave secreta para firmar tokens JWT.

El resto de variables ya tienen valores por defecto.

> **Nota**: Si los puertos 9200, 8001 o 8000 están ocupados, puede cambiarlos modificando `ELASTICSEARCH_PORT_HOST`, `CHROMA_PORT_HOST` o `APP_PORT_HOST` en el `.env`.

## 🐳 Ejecución con Docker Compose

El proyecto incluye un archivo `docker-compose.yml` que levanta todos los servicios necesarios:

- `app`: API FastAPI del sistema.
- `elasticsearch`: motor de búsqueda léxica (índice invertido).
- `chroma`: base de datos vectorial para embeddings.

### 1. Iniciar todos los servicios

```bash
docker compose up --build
```

### 2. Poblar las bases de datos

El proyecto incluye un corpus inicial de **2500 documentos** en formato JSONL (`data/initial_corpus.jsonl`). Los siguientes scripts procesan este corpus y lo distribuyen en los sistemas de almacenamiento:

- **populate_elasticsearch.py**: Indexa los documentos en Elasticsearch para búsqueda esparcida 
- **populate_chromadb.py**: Genera embeddings semánticos y almacena los chunks en ChromaDB para búsqueda densa

Ejecute ambos scripts mientras los servicios están activos:

```bash
docker compose exec app python scripts/populate_elasticsearch.py

docker compose exec app python scripts/populate_chromadb.py
```

## Interfaz visual

Contamos con una interfaz visual que correrá de forma independiente. Para su integración, siga los pasos del README interno de su repositorio:

- [Interfaz visual del proyecto](https://github.com/AmandaMedina17/News_Retrieval_UI)

## 🤝 Contribución

1. Cree una rama para su funcionalidad: `git checkout -b feature/nueva-funcionalidad`
2. Realice commits descriptivos siguiendo convenciones (ej. `feat: add new search endpoint`)
3. Envíe un Pull Request.

## 📝 Notas

- Asegúrese de activar el entorno virtual antes de ejecutar cualquier comando.
- Si encuentra errores, verifique las versiones de dependencias y configuraciones en `.env`.
- Para soporte, revise los documentos en `docs/` o abra un issue.
