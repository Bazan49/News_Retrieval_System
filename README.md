# Sistema de Recuperación de Noticias

Sistema de Recuperación de Información (SRI) diseñado para explorar, buscar y recuperar artículos de noticias usando técnicas modernas de recuperación de información.

## 📁 Estructura del Proyecto

```
News_Retrieval_System/
├── data/                 # Datos iniciales (JSONL, etc.)
├── docs/                 # Documentación (Chunking_strategy.md, etc.)
├── scripts/              # Scripts para poblar bases de datos
├── src/                  # Código fuente
│   ├── API/              # Endpoints FastAPI
│   ├── EmbeddingsModule/ # Chunking y embeddings
│   ├── IndexModule/      # Indexación
│   ├── RetrievalModule/  # Recuperación
│   └── main.py           # Punto de entrada de la API
├── tests/                # Pruebas unitarias
├── venv_sri/             # Entorno virtual
├── .env.example          # Ejemplo de configuraciones
└── README.md             # Este archivo
```


## 🚀 Inicio 

Sigue estos pasos para configurar y ejecutar el proyecto localmente.

### Prerrequisitos

- **Python 3.8+**: Asegúrate de tener Python instalado. Verifica con `python --version`.
- **Git**: Para clonar el repositorio.
- **Docker**: Necesario para ejecutar los contenedores de Elasticsearch y ChromaDB.


### 1. Clonación del Repositorio

### 2. Creación del Entorno Virtual

Crea y activa un entorno virtual para aislar las dependencias:

```bash
# Crear entorno virtual
python -m venv venv_sri

# Activar en Windows
venv_sri\Scripts\activate

```

### 3. Instalación de Dependencias

Instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```
### 4. Configuración del Entorno

1. Copia el archivo de ejemplo de configuración:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` con tus configuraciones (ej. claves de API, puertos, rutas):

### 5. Levantar Servicios con Docker (Elasticsearch y ChromaDB)
Para que el sistema funcione completamente, necesitas dos servicios externos.

> Importante: los puertos expuestos por los contenedores deben coincidir con los valores configurados en tu `.env` para Elasticsearch y ChromaDB. Si configuras un puerto distinto en `.env`, usa ese mismo puerto en el comando `docker run`.

### 🐳 Elasticsearch con Docker

Para el almacenamiento y búsqueda tradicional (índice invertido), utilizamos **Elasticsearch** en su versión **9.3.3**. La forma más rápida y fiable de tenerlo listo es mediante su imagen oficial de Docker.

#### 📚 Referencia

Este procedimiento sigue la [guía oficial de Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html). Si deseas profundizar en el concepto o solucionar problemas, te recomiendo el siguiente [video explicativo](https://youtu.be/XBEZedFW4MI?si=rYLUaFswXkjOJb6t).

### 📌 Comandos utilizados (Elasticsearch)

A continuación se muestran los comandos específicos que se usaron para poner en marcha Elasticsearch, junto con una breve descripción de cada uno.

| Comando | Explicación |
| :--- | :--- |
| `docker network create elastic` | Crea una red interna llamada `elastic` (tipo bridge). Esta red permite que múltiples contenedores (por ejemplo, Elasticsearch y Kibana) se comuniquen entre sí usando sus nombres como si fueran direcciones IP. Si planeas usar Kibana más adelante, es muy recomendable. |
| `docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:9.3.3` | Ejecuta un contenedor llamado `es01` conectado a la red `elastic`. Publica el puerto `9200` para acceder a la API REST, inicia en modo interactivo (`-it`) y limita la RAM a `1GB`. La opción `-it` muestra los logs en la terminal; si prefieres ejecutarlo en segundo plano, puedes sustituir `-it` por `-d`. |

> **Nota sobre la red `elastic`**: Aunque el proyecto actual solo necesita Elasticsearch, hemos creado esta red porque es útil si en el futuro añades Kibana (panel de visualización) o si quieres conectar otras herramientas de Elastic Stack. Sin la red, igualmente podrías ejecutar Elasticsearch con `-p 9200:9200` sin `--net elastic`; la red añade aislamiento y facilita la comunicación entre servicios.


### 🐳 ChromaDB con Docker

#### 📚 Referencia

Este procedimiento sigue la [guía oficial de ChromaDB para despliegue con Docker](https://docs.trychroma.com/guides/deploy/docker). Si deseas profundizar en la configuración consulta la documentación oficial.

Ejecuta el siguiente comando para iniciar ChromaDB en modo servidor con persistencia de datos:

```bash
docker run -d --name chroma-server -p 8001:8000 -v chroma_data:/data -e IS_PERSISTENT=TRUE chromadb/chroma
```

### 📂 6. Población de las Bases de Datos

Una vez que los contenedores de Elasticsearch y ChromaDB estén corriendo, debes cargar los documentos en ambos sistemas.

### Corpus inicial

El proyecto ya incluye un corpus de 2500 documentos en formato JSONL (data/initial_corpus.jsonl). Si necesitas generar más noticias, consulta la documentación del módulo de adquisición de datos (DataAcquisitionModule).

### Poblar Bases de Datos

Ejecuta los scripts para cargar los datos:

```bash
# Poblar Elasticsearch
python scripts/populate_elasticsearch.py

# Poblar ChromaDB con embeddings
python scripts/populate_chromadb.py

```

> **Nota:** El script de ChromaDB procesa solo 10 documentos por defecto para pruebas rápidas. Para indexar todos los 2500 documentos, abre el script y cambia la variable N = 0 o comenta la línea de limitación.

Ambos scripts leerán el archivo data/initial_corpus.jsonl y almacenarán la información en sus respectivas bases de datos.

## 🏃‍♂️ Ejecución del Proyecto

### Ejecutar la API

Inicia el servidor FastAPI:

```bash
uvicorn src.main:app --reload
```

- Accede a la documentación interactiva en: `http://localhost:8000/docs`
- Endpoints disponibles: búsqueda semántica, híbrida, etc.

### Interfaz visual en desarrollo

Además de la API FastAPI, se está construyendo una interfaz visual que correrá de forma independiente. Para ver cómo lanzar esa interfaz, revisa el README interno del repositorio de la interfaz visual en el siguiente enlace:

- [Interfaz visual del proyecto](https://github.com/AmandaMedina17/News_Retrieval_UI)

## 🔧 Configuración Avanzada

- **Modelos de Embeddings**: Cambia `EMBEDDING_MODEL` en `.env` para usar diferentes modelos (ej. `intfloat/multilingual-e5-large`).
- **Chunking**: Ajusta `CHUNKER_MAX_TOKENS` y `OVERLAP_PERCENT` para optimizar la división de documentos.
- **Bases de Datos**: Configura hosts y puertos en `.env` para Elasticsearch y ChromaDB.

## 🤝 Contribución

1. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Realiza commits descriptivos siguiendo convenciones (ej. `feat: add new search endpoint`)
3. Envía un Pull Request.

## 📝 Estado del proyecto

- ✅ Módulo de adquisición de datos (indexación inicial de contenido)
- ✅ Adquisición e indexación en Elasticsearch
- ✅ Base de datos vectorial con ChromaDB y embeddings Jina
- ✅ Modelo LMIR (Language Model con suavizado de Dirichlet)
- ✅ Búsqueda esparcida (Elasticsearch, basada en índice invertido)
- ✅ Búsqueda densa (ChromaDB, basada en embeddings semánticos)
- ✅ Búsqueda híbrida con RRF (combinación de esparcida y densa)
- ✅ Endpoints API
- ⏳ Módulo RAG (en desarrollo)
- ⏳ Búsqueda web externa (pendiente de integrar)
- ⏳ Módulo de expansión y retroalimentación (en desarrollo)
- ⏳ Interfaz visual (en desarrollo)
- ⏳ Módulo de posicionamiento y ranking visual (pendiente)

## 📝 Notas

- Asegúrate de activar el entorno virtual antes de ejecutar cualquier comando.
- Si encuentras errores, verifica las versiones de dependencias y configuraciones en `.env`.
- Para soporte, revisa los documentos en `docs/` o abre un issue.

**Última actualización**: Abril 2026