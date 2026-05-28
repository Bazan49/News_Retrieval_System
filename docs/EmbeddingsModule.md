# Módulo de Embeddings

El **Módulo de Embeddings** es el componente encargado de generar representaciones vectoriales (embeddings) de los fragmentos textuales (chunks) y gestionar su almacenamiento y recuperación en una base de datos vectorial. Estas representaciones permiten la **búsqueda semántica**, complementando la búsqueda léxica tradicional al capturar el significado profundo de los textos.

Se utiliza **ChromaDB** como base de datos vectorial subyacente y el modelo **`jinaai/jina-embeddings-v2-base-es`** para la generación de embeddings.

## Arquitectura y componentes principales

El módulo sigue los principios de **Arquitectura Limpia** (Clean Architecture), garantizando la separación de responsabilidades y la independencia tecnológica:

- **Capa de dominio**: Define dos contratos abstractos fundamentales:
  - `BaseVectorStore`: declara las operaciones de persistencia vectorial (`add`, `search`, `delete`). Es la interfaz que debe implementar cualquier base de datos vectorial (ChromaDB, FAISS, etc.).
  - `BaseEmbedder`: declara la generación de embeddings (`encode`, `encode_single`, `dim`). Permite abstraer el modelo concreto de embeddings (Jina, Sentence Transformers, etc.).

- **Capa de infraestructura**: Implementa los contratos con tecnologías concretas:
  - `ChromaVectorStore`: implementa `BaseVectorStore` usando el cliente asíncrono de ChromaDB. Gestiona la colección con espacio de búsqueda `hnsw:space: "cosine"` para usar similitud del coseno.
  - `SentenceTransformerEmbedder`: implementa `BaseEmbedder` utilizando `sentence-transformers` con el modelo configurado (soporta backend opcional, como ONNX). 
- **Capa de aplicación**: Alberga los casos de uso que orquestan la lógica del módulo, por ejemplo:
  - `VectorIndexer`: se encarga de tomar una lista de `Chunk` (provenientes del módulo de segmentación), generar sus embeddings y almacenarlos en la base de datos vectorial. Procesa los chunks en lotes para optimizar el rendimiento.
  - `VectorSearcher`: implementa la búsqueda semántica. Recibe una consulta textual, la transforma a vector con el embedder y ejecuta la búsqueda por similitud en la base de datos vectorial, devolviendo los resultados más relevantes envueltos en objetos `RetrievalResult`.

La **inyección de dependencias** se gestiona mediante el contenedor `EmbeddingsContainer` construido con la librería **`dependency-injector`**, que registra y resuelve las dependencias del módulo de forma centralizada.

## Modelo de embeddings: `jinaai/jina-embeddings-v2-base-es`

Para la generación de embeddings se ha seleccionado el modelo **`jina-embeddings-v2-base-es`** de Jina AI. Las razones de esta elección están directamente vinculadas a sus características técnicas:

- **Entrenamiento específico para español**: el modelo ha sido entrenado para ofrecer un alto rendimiento en el idioma español (además de soporte para inglés), lo que garantiza una representación semántica de calidad para nuestro corpus de noticias en español, capturando correctamente los matices y expresiones del lenguaje periodístico.
- **Vectores de 768 dimensiones**: proporciona un equilibrio óptimo entre riqueza semántica y eficiencia computacional. Es lo suficientemente expresivo para capturar matices del lenguaje noticioso, pero no tan grande como para ralentizar las búsquedas por similitud en ChromaDB.
- **Longitud de secuencia de 8192 tokens**

La generación de embeddings se realiza mediante la librería `sentence-transformers`. Para mejorar el rendimiento, se ha configurado el backend ONNX (variable `EMBEDDING_BACKEND=onnx`), que acelera la inferencia sin pérdida apreciable de precisión.

## Búsqueda por similitud y base de datos vectorial

Hemos configurado ChromaDB para que almacene todos los embeddings generados en una **colección** con el espacio de búsqueda `hnsw:space: "cosine"`. La métrica de similitud empleada es la **similitud del coseno**, que mide el coseno del ángulo entre dos vectores, ignorando su magnitud. Esta métrica es especialmente adecuada para embeddings de texto, ya que captura la orientación semántica de los documentos, reflejando si apuntan en la misma dirección conceptual.

La distancia coseno (que ChromaDB utiliza internamente) se calcula como:

$$
d = 1.0 - \frac{\sum (A_i \times B_i)}
{\sqrt{\sum (A_i^2)} \cdot \sqrt{\sum (B_i^2)}}
$$

### HNSW: índice vectorial para búsqueda aproximada

**HNSW (Hierarchical Navigable Small World)** es el algoritmo de índice vectorial por defecto que utiliza ChromaDB. Se trata de una estructura de datos basada en grafos diseñada para la **búsqueda aproximada del vecino más cercano (ANN)** en espacios vectoriales de alta dimensionalidad.

Un índice HNSW funciona construyendo un grafo de múltiples capas:
- Cada capa contiene un subconjunto de los puntos de datos.
- Las capas superiores son más dispersas y actúan como "autopistas" que permiten una navegación rápida a grandes saltos.
- El algoritmo conecta puntos cercanos en cada capa, creando propiedades de "mundo pequeño" (small-world) que posibilitan una complejidad de búsqueda eficiente.

Durante la búsqueda:
1. Se comienza en la capa superior y se navega hacia el punto de consulta en el espacio de embeddings.
2. Se desciende a través de capas sucesivas, refinando la búsqueda en cada nivel.
3. Finalmente, se alcanzan los vecinos más cercanos en la capa inferior, que contiene todos los puntos.

Gracias a esta estructura jerárquica, la búsqueda de los `k` vectores más similares se realiza con una complejidad logarítmica **O(log n)**, sin necesidad de recorrer todos los vectores del corpus (lo que sería inviable para colecciones grandes).

## Limitaciones y consideraciones

A pesar de las ventajas de la búsqueda semántica, el enfoque actual presenta ciertas limitaciones:

- **Requisitos de hardware**: el modelo `jina-embeddings-v2-base-es` (161 millones de parámetros) funciona correctamente en CPU para volúmenes pequeños, pero la generación de embeddings por lotes puede ser lenta en hardware convencional. Para mayor velocidad se recomienda una GPU. 
- **Dependencia del modelo**: cambiar el modelo de embeddings (por ejemplo, para mejorar la calidad semántica) implica **reindexar todo el corpus** desde cero, ya que los vectores antiguos no son compatibles.
- **Dependencias externas**: el módulo descarga los archivos necesarios desde Hugging Face Hub la primera vez que se ejecuta. Esto puede demorar o fallar en dependencia de la conexión a internet.

Estas limitaciones no invalidan la utilidad del módulo, pero deben tenerse en cuenta al planificar el despliegue y el mantenimiento del sistema.


## Referencias

1. Jina AI. (2023). *jina-embeddings-v2-base-es: A bilingual embedding model for Spanish and English*. Recuperado de https://huggingface.co/jinaai/jina-embeddings-v2-base-es
2. ChromaDB. (2024). *Chroma: The AI-native open-source embedding database*. Recuperado de https://docs.trychroma.com
