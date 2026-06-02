# Módulo RAG (Retrieval-Augmented Generation)

La **generación aumentada por recuperación (RAG)** es una técnica que combina generación de texto con recuperación de información para mejorar la calidad, precisión y actualidad de las respuestas generadas por modelos de lenguaje. En lugar de confiar únicamente en el conocimiento estático del modelo (limitado a su fecha de entrenamiento), RAG consulta fuentes externas en tiempo real, recupera fragmentos relevantes y los integra en el prompt, anclando así la respuesta a evidencia verificable.

En nuestro proyecto, el **módulo RAG** es el componente central que **implementa la generación** y **orquesta la recuperación**. De esta forma, coordina la ejecución de estos componentes en el orden correcto, garantizando que el modelo de lenguaje reciba siempre el conjunto de fragmentos más relevante disponible.

El flujo del pipeline sigue el patrón **pregunta más contexto** (query‑based): la consulta del usuario se concatena directamente con la información recuperada para formar el prompt de entrada. 

## Flujo completo del sistema (end-to-end)

1. **Entrada del usuario.** El proceso comienza cuando el usuario escribe una consulta en lenguaje natural, por ejemplo: “¿Qué países de América Latina tienen deuda con el FMI?”. Esta consulta es el punto de partida y activa todo el pipeline del sistema.

2. **Búsqueda local fusionada con RRF.** El sistema ejecuta en paralelo la búsqueda léxica y la búsqueda semántica. Ambas listas de resultados se combinan mediante el algoritmo RRF (Reciprocal Rank Fusion), obteniendo así un ranking inicial equilibrado entre relevancia textual y semántica.

3. **Activación de búsqueda web si los resultados locales son insuficientes.** Se evalúa si los documentos obtenidos localmente son suficientes en cantidad y calidad. Si no es así, el sistema lanza automáticamente una búsqueda en Google News RSS, recupera noticias recientes, las procesa y las añade al conjunto de resultados. Esta ampliación permite responder a consultas sobre temas muy actuales o poco cubiertos en el corpus local.

4. **Re‑ranking con cross‑encoder sobre los primeros N resultados.** Sobre los primeros N documentos se aplica un modelo cross‑encoder, que evalúa pares (consulta, documento) de forma más precisa que las búsquedas iniciales. Este modelo produce una nueva puntuación de relevancia que corrige posibles imprecisiones de la fusión RRF, mejorando la calidad de los resultados más prometedores.

5. **Posicionamiento final.** Se calcula el `final_score` de cada documento combinando tres factores: la relevancia base (RRF o cross‑encoder), la similitud con el perfil del usuario (personalización) y la frescura. 

6. **Generación de la respuesta.** El modelo de lenguaje genera una respuesta enriquecida a partir del prompt que contiene los fragmentos recuperados.

7. **Salida del sistema.** Finalmente, se devuelve al usuario la respuesta generada junto con los documentos ordenados.

Dentro de nuestra arquitectura, el módulo RAG no implementa internamente las fases de recuperación, fusión, re‑ranking o activación de búsqueda web. Estas etapas (pasos 2 a 5 del pipeline) son delegadas a otros módulos especializados. De esta forma, el módulo RAG se mantiene desacoplado y se centra exclusivamente en la generación de la respuesta, permitiendo que cada componente pueda escalar, actualizarse o sustituirse de manera independiente, mejorando la mantenibilidad y la flexibilidad del sistema.

## Arquitectura y componentes principales

El módulo RAG sigue una **arquitectura limpia** con tres capas bien diferenciadas y una clara separación de responsabilidades:

- **Capa de dominio**: Define los objetos centrales (`RAGResult`, `RAGContextItem`) y las interfaces para la generación (`BaseGenerator`).
- **Capa de infraestructura**: Implementa el generador concreto (`MistralGenerator`).
- **Capa de aplicación**: Contiene los servicios que orquestan el pipeline:
  - `RetrieverService`: responsable de la recuperación de documentos (búsqueda híbrida, fusión RRF, web, re‑ranking y posicionamiento).
  - `RAGGeneratorService`: Construye el contexto, genera los prompts y llama al LLM para obtener la respuesta.
  - `RAGOrchestratorService`: Orquesta todo el pipeline del sistema desde que el usuario formula una pregunta hasta que obtiene la respuesta enriquecida y los documentos fuente.

La **inyección de dependencias** se centraliza en `RAGContainer`.

## Componente generador

Una vez recuperados y ordenados los documentos más relevantes, la última etapa del sistema RAG consiste en generar una respuesta en lenguaje natural a partir de dicha información. Para ello se emplea un modelo de lenguaje de gran tamaño (LLM), cuya función es sintetizar la evidencia recuperada y producir una respuesta coherente y fundamentada.

Con el objetivo de maximizar la calidad de las respuestas generadas, el sistema no envía únicamente la consulta del usuario y los documentos recuperados. En su lugar, se construye un prompt estructurado que proporciona al modelo tanto el contexto necesario para responder como instrucciones explícitas sobre el comportamiento esperado.

## Construcción del prompt

El prompt se compone de dos elementos principales:

- **Mensaje del sistema**, donde se definen las directrices generales de generación, incluyendo el idioma de respuesta, la necesidad de basarse en la evidencia proporcionada y el tratamiento de situaciones en las que la información disponible sea insuficiente.
- **Mensaje del usuario**, que contiene los fragmentos recuperados junto con la consulta original. Los documentos se presentan de forma estructurada y acompañados de metadatos relevantes, facilitando su identificación y utilización durante la generación: 

<div style="display: flex; gap: 20px;">

  <div style="flex: 1; font-family: monospace;">
    
[1]  
Fuente: {source}  
Fecha: {date}  
Título: {title}  
Contenido: {content}

[2] 

...
  </div>

</div>

## Configuración del proceso de decodificacion

Además de la estructura del prompt, el sistema ajusta diversos parámetros del modelo para controlar el estilo y comportamiento de las respuestas generadas.

- **Temperatura**: La temperatura controla el grado de aleatoriedad durante la generación del texto. Valores bajos favorecen respuestas más deterministas y consistentes, mientras que valores más altos producen respuestas más variadas, aunque potencialmente menos estables. En este sistema se utiliza **`temperature = 0.3`**, un valor relativamente bajo que prioriza la coherencia y la fidelidad al contexto recuperado, aspectos especialmente importantes en el dominio periodístico. Al mismo tiempo, mantiene un cierto nivel de variabilidad léxica que contribuye a generar respuestas más naturales y menos repetitivas.

- **Top-p**: El parámetro top‑p restringe el conjunto de palabras candidatas a aquellas cuya probabilidad acumulada supera un umbral dado. En lugar de considerar todas las palabras posibles, el modelo selecciona solo el subconjunto más probable que acumula. Esto evita palabras extremadamente improbables y mejora la fluidez de la respuesta. Se emplea **`top_p = 0.95`**, un valor estándar que equilibra cobertura y coherencia.

- **Penalizaciones por repetición**: Para evitar respuestas redundantes, se aplican mecanismos que reducen la probabilidad de reutilizar repetidamente las mismas palabras o expresiones durante la generación. En concreto, se utilizan los parámetros **`frequency_penalty = 0.5`** y **`presence_penalty = 0.3`**, favoreciendo una redacción más variada y fluida sin comprometer la coherencia de la respuesta.

- **Máximo de tokens**: El parámetro **`max_tokens`** limita la longitud máxima de la respuesta generada. Establecimos el límite en **`700`** tokens para garantizar que el modelo tenga suficiente espacio para generar respuestas completas y coherentes, evitando cortes abruptos.

## Selección del modelo generativo

El sistema utiliza la infraestructura de inferencia proporcionada por `Mistral AI` y el modelo `mistral-small-latest`. La elección de esta combinación responde a varios factores: su buen rendimiento en tareas de comprensión y generación en español, la baja latencia ofrecida por la plataforma (esencial en aplicaciones interactivas), y la facilidad de integración.

## Configurabilidad y extensibilidad

Todos los parámetros del generador, así como el modelo y el proveedor, son configurables mediante variables de entorno (archivo `.env`). Esto permite ajustar el comportamiento del sistema sin modificar el código, facilitando la experimentación y el ajuste fino. 

