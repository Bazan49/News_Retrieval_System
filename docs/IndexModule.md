# Módulo de Indexación

El Módulo de Indexación es el componente encargado de transformar los documentos previamente adquiridos y segmentados (chunks) en estructuras de datos eficientes que permitan la recuperación rápida de información. En el contexto del sistema de noticias, su salida principal es un **índice invertido** persistente que será consultado por la fase de recuperación, ya sea de forma independiente o como parte de una estrategia de **búsqueda híbrida** (combinando la relevancia léxica con la semántica de los embeddings vectoriales).

Se utiliza **Elasticsearch** como sistema subyacente para construir, almacenar y gestionar el índice invertido, ya que este proporciona una capa de persistencia eficiente y escalable, optimizada para búsquedas de texto.

## Arquitectura y componentes principales

El módulo de indexación sigue los principios de **Arquitectura Limpia** (Clean Architecture), lo que garantiza la separación de responsabilidades, la independencia tecnológica y la testabilidad. Las capas se organizan de la siguiente manera:

- **Capa de dominio**: Contiene los **objetos de negocio puros**, como `SearchDocument`, que representan los datos indexables y sus metadatos. No dependen de ninguna tecnología externa. Además, define los **contratos abstractos** que debe cumplir cualquier infraestructura. El contrato principal es `IndexRepository`, que declara las operaciones necesarias para gestionar el índice.
- **Capa de infraestructura**: Implementa los contratos anteriores con tecnologías concretas. La implementación principal es `ElasticsearchIndexRepository`, que utiliza el cliente de Elasticsearch (asíncrono) y el archivo `mapping.json` para gestionar el índice invertido.
- **Capa de aplicación**: Alberga los casos de uso, como `IndexingService`, el cual orquesta la lógica de indexación (asegurar el índice, transformar los datos, indexar en lote y refrescar). También incluye el **mapeador** (`ChunkDocumentProcessor`), cuya responsabilidad es convertir las entidades externas (`Chunk` proveniente del módulo de segmentación) en entidades propias del dominio (`SearchDocument`). De esta forma, el dominio no se contamina con dependencias de otros módulos; solo se modifica el mapeador (de ser requerido), sin afectar al resto del código.

La **inyección de dependencias** se gestiona mediante un contenedor (`SearchContainer`) construido con la librería **`dependency-injector`**, que registra y resuelve todas las dependencias del módulo de forma centralizada (cliente de Elasticsearch, repositorio, servicio de indexación, etc.).

## El índice invertido: estructura y proceso de construcción

El corazón del módulo de indexación es el **índice invertido**, una estructura que asocia cada término con los documentos que lo contienen. Elasticsearch construye y mantiene el índice automáticamente según la configuración definida en `mapping.json`, siguiendo las fases clásicas del proceso de indexación.

**Campos indexados**: solo los campos de tipo `text` (`title` y `content`) pasan por el analizador y generan términos que forman parte del índice invertido. El resto de los campos (`chunk_id`, `source`, `url`, `authors`, `date`, `chunk_number`) se definen como `keyword` o `date`; se almacenan como metadatos para su uso en filtros o resultados, pero **no contribuyen al índice invertido**.

### 1. Extracción de unidades indexables (análisis del texto)

Cuando un `SearchDocument` llega a Elasticsearch, sus campos `content` y `title` pasan por un **analyzer** personalizado llamado `spanish_analyzer`. Este analyzer realiza:

- **Tokenización**: divide el texto en tokens usando el tokenizador `standard` (separa por palabras, elimina puntuación).
- **Normalización**: convierte todo a minúsculas (`lowercase`).
- **Filtrado**: elimina palabras vacías del español (artículos, preposiciones, etc.) mediante la lista `spanish_stop`.
- **Stemming**: reduce variantes morfológicas a una raíz común usando `spanish_stemmer` (ej. "corriendo" → "corr").

El resultado es una lista de **términos** (unidades indexables) que formarán el vocabulario del índice.

### 2. Construcción del índice invertido (posting lists)

Para cada término extraído, Elasticsearch crea una **posting list** que contiene, al menos, los identificadores de los documentos (`_id` del chunk) y la frecuencia del término dentro de cada documento.

Simultáneamente, Elasticsearch mantiene estadísticas globales por segmento: número total de documentos, frecuencia documental de cada término (`df`), longitud de cada documento y la longitud promedio del corpus (esenciales para modelos de ranking como BM25 o LMIR).

### 3. Compresión del índice

Para minimizar el espacio en disco, Elasticsearch aplica compresión sobre las posting lists. Estas técnicas reducen drásticamente el tamaño del índice. Por ejemplo:

- **Front-coding** en el diccionario de términos para aprovechar prefijos comunes (ej. "automat", "automatic", "automation" se comprimen compartiendo "automat").

### 4. Almacenamiento y distribución

El índice se persiste en disco como una colección de **segmentos inmutables**. Elasticsearch distribuye estos segmentos en **shards** y **réplicas**. En nuestro proyecto educativo usamos un solo shard y cero réplicas para simplificar. Tanto el número de shards como de réplicas pueden ajustarse para escalar en producción.

### 5. Actualización dinámica

Cuando se incorporan nuevos documentos al índice (ya sea para añadir, actualizar o eliminar), el sistema no reconstruye el índice completo desde cero. En su lugar, se aplican estrategias de **actualización incremental** que añaden los cambios en estructuras auxiliares, marcan las versiones obsoletas y, periódicamente, reorganizan y compactan los datos para mantener la eficiencia. Esto permite altas tasas de escritura sin degradar el tiempo de respuesta de las búsquedas.