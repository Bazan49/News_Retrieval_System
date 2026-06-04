# Módulo de Adquisición de Datos

El **Módulo de Adquisición de Datos** es el punto de entrada de todo el sistema. Su responsabilidad es **recolectar y extraer contenido de fuentes web de noticias** de manera inteligente y respetuosa, transformándolo en un conjunto inicial de documentos estructurados sobre el que luego se construirá el índice invertido y los embeddings vectoriales.

## Estadísticas del corpus

Tras la ejecución del módulo de adquisición, se ha recopilado un corpus de **2.500 artículos** (en `data/initial_corpus.jsonl`) con las siguientes características:

- **Documentos totales**: 2.500
- **Longitud del contenido**: media de 6107 caracteres (≈985 palabras), desviación estándar de 5881 caracteres (alta variabilidad).
- **Distribución por fuente**:
  | Fuente | Artículos | Porcentaje |
  |--------|-----------|------------|
  | lanacion.com.ar | 913 | 36.5% |
  | bbc.com | 470 | 18.8% |
  | presidencia.gob.cu | 438 | 17.5% |
  | actualidad.rt.com | 369 | 14.8% |
  | telemundo.com | 300 | 12.0% |
  | foodit.lanacion.com.ar | 10 | 0.4% |
- **Rango de fechas**: desde el **21 de diciembre de 2012** hasta el **17 de abril de 2026** (periodo de 4865 días).

Estas cifras demuestran un volumen suficiente y una diversidad temática y temporal adecuada para evaluar las estrategias de recuperación del sistema.

## Componentes principales

El módulo organiza sus componentes en torno a un servicio principal (`DataAcquisitionService`) que orquesta el crawler, el scraper y el almacenamiento de noticias. Cada componente tiene una responsabilidad bien definida, lográndose de esta forma una clara separación de tareas.

### Web Crawler

El crawler implementa un recorrido **FIFO** sobre las URLs pendientes. Las URLs semilla se cargan inicialmente en la cola (`frontier`). Cada URL se procesa si cumple con las restricciones de profundidad y si el dominio lo permite según `robots.txt`.

- **RobotsManager**: Consulta `robots.txt` del dominio antes de descargar. Si el archivo prohíbe el acceso, la URL se descarta.
- **FrontierManager**: Mantiene dos listas CSV: `frontier.csv` (URLs por procesar) y `visited.csv` (URLs ya procesadas o descartadas). Esto permite continuar un crawler interrumpido.
- **URLFilter**: Filtra enlaces para no salirse del dominio semilla o para rechazar formatos no deseados (imágenes, PDF, etc.).

### Componentes de red (Fetcher)

El módulo `network` proporciona la capacidad de descargar páginas web de manera robusta y extraer enlaces.

- **`Fetcher.fetch()`** – descarga una página con reintentos inteligentes:

  1. Reintenta solo para errores transitorios (timeout, error de conexión, códigos 5xx). Los errores 4xx (incluyendo 403) abortan inmediatamente.
  2. Usa un timeout de 8 segundos y hasta 3 reintentos con 2 segundos de espera.
  3. Devuelve el texto HTML o `None` si la descarga falla.

- **`Fetcher.extract_links()`** – extrae todos los enlaces absolutos (que comiencen con `http`) del HTML descargado, usando BeautifulSoup.

### Arquitectura de scrapers

El sistema de scraping está organizado en tres niveles:

- **Interfaz `IScraper`**: define el contrato `extract(url, html) -> ScrapedDocument`.
- **Lógica común en `BaseScraper`**: implementa el flujo general usando `newspaper3k` y `BeautifulSoup`. Extrae título, contenido, autores y fecha; valida que la página sea un artículo real (meta `og:type=article`) y que el contenido tenga al menos 500 caracteres.
- **Scrapers especializados**: derivan de `BaseScraper` y sobrescriben métodos para dominios concretos.

**Selección del scraper adecuado**  
La `ScraperFactory` devuelve un scraper basado en el dominio de la URL. Si el dominio está en el diccionario de mapeo, se instancia el scraper especializado; en caso contrario, se usa `BaseScraper`.

### Almacenamiento y persistencia

El repositorio `JSONLRepository` implementa la interfaz `IDocumentRepository` y escribe los documentos en un archivo **JSONL** (una línea por artículo). Los documentos se acumulan en un búfer y se vuelcan al disco cada `batch_size` elementos o al final del proceso.

## DataAcquisitionService: orquestador del proceso de adquisición

### Parámetros de configuración:
- `max_pages` (por defecto `50`): número máximo de páginas a descargar (para evitar bucles infinitos).
- `max_depth` (por defecto `3`): profundidad máxima del crawling, contada desde la URL semilla.
- `delay` (por defecto `1`): segundos de espera entre descargas, para respetar los servidores.
- `batch_size` (por defecto `10`): número de documentos que se acumulan en memoria antes de escribir al archivo.
- `output_file` (por defecto `"data/corpus.jsonl"`): ruta del archivo JSONL de salida.

### Flujo de ejecución completo

1. Creación del servicio con parámetros (`max_pages`, `max_depth`, `delay`, `batch_size`, `output_file`).
2. Ejecución del crawler: se cargan las URLs semilla desde `data/seeds.csv` al `frontier` (o se recupera la frontier persistente desde ejecuciones anteriores) y se inicia el recorrido.
3. Por cada URL extraída:
   - Se consulta `robots.txt` (usando `RobotsManager`).
   - Se descarga el HTML mediante `Fetcher.fetch()`.
   - Se extraen nuevos enlaces y se añaden a la frontier (si la profundidad actual < `max_depth`).
   - Se obtiene el scraper adecuado de `ScraperFactory`.
   - Se extraen los metadatos y el contenido (si el documento es válido).
   - Se guarda en el repositorio.
4. Periódicamente (cada `batch_size`) y al finalizar, se escribe el búfer en el archivo JSONL.
5. Se actualizan los archivos `frontier.csv` y `visited.csv` para poder continuar más tarde.

## Extrayendo más noticias

El script `scripts/collector.py` permite ejecutar el `DataAcquisitionService` con parámetros personalizados. Por ejemplo:

```bash
python scripts/collector.py --max-pages 100 --max-depth 2 --delay 2 --output data/new_corpus.jsonl
```

### Reiniciar o continuar 

El crawler guarda su estado en `src/DataAcquisitionModule/crawler/data/`:

1. `frontier.csv`: URLs pendientes.
2. `visited.csv`: URLs ya procesadas.
3. `seeds.csv`: URLs semillas.

**Reinicio total**: borrar `frontier.csv` y `visited.csv`, actualizar `seeds.csv`, ejecutar el script.

**Continuar**: dejar los archivos intactos; el crawler retomará desde donde se detuvo.
