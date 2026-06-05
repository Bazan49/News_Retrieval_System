# Módulo de Ranking (Posicionamiento)

El **Módulo de Ranking** es el componente encargado de establecer el orden final en el que se presentan los documentos recuperados al usuario. Su función principal es transformar un conjunto de candidatos relevantes en una lista ordenada, optimizada según múltiples criterios de calidad y utilidad.

## Arquitectura y componentes principales

El módulo sigue una **arquitectura limpia** con capas bien diferenciadas:

- **Capa de dominio**: Define los contratos para las estrategias de puntuación y de re‑ranking.
  - `HybridSearchResult` es el objeto central que representa un resultado de búsqueda una vez fusionadas las contribuciones dispersas y densas. Encapsula la información del documento original (`RetrievalResult`), las puntuaciones individuales, los factores de ranking y el `final_score` resultante del posicionamiento. Es la unidad que se utiliza en todas las fases de ranking y se devuelve finalmente al usuario.
  - `ScoringStrategy`: interfaz para estrategias que calculan un factor numérico y lo asignan a un campo específico de `HybridSearchResult` (sin modificar el orden).
  - `RankingStrategy`: interfaz para estrategias que reordenan la lista de resultados (por ejemplo, cross‑encoder).
  - `FusionStrategy`: contrato para fusionar dos listas de resultados (dispersa y densa) en una sola lista híbrida.

- **Capa de infraestructura**: Implementaciones concretas de las estrategias:
  - `RecencyScoringStrategy`: calcula el factor de actualidad (`recency_factor`) mediante decaimiento exponencial.
  - `PersonalizationScoringStrategy`: calcula la similitud coseno entre el perfil del usuario y cada documento (`personalization_similarity`).
  - `CrossEncoderRankingStrategy`: utiliza un modelo cross‑encoder para re‑ordenar los resultados.
  - `RRFFusionStrategy`: implementa la fusión mediante RRF.

- **Capa de aplicación**: Servicios que orquestan el pipeline de ranking.
  - `RankingService`: recibe una lista de resultados, aplica todas las `ScoringStrategy` inyectadas, normaliza la relevancia base (RRF o cross‑encoder) y la similitud de personalización mediante min‑max, combina linealmente los factores y ordena por `final_score`.
  - `FusionService` (parte del ranking híbrido): se encarga únicamente de fusionar los resultados dispersos y densos.

La **inyección de dependencias** se centraliza en `RankingContainer`.

## Búsqueda híbrida (Reciprocal Rank Fusion)

Los sistemas de recuperación basados exclusivamente en coincidencias léxicas son especialmente efectivos cuando las consultas contienen términos específicos, nombres propios o expresiones técnicas presentes en los documentos. Sin embargo, su rendimiento disminuye cuando el usuario emplea sinónimos o formulaciones diferentes a las utilizadas en el corpus. Por otro lado, los métodos de recuperación semántica basados en embeddings permiten identificar documentos relacionados conceptualmente con la consulta, aunque pueden perder precisión ante términos muy específicos o poco frecuentes.

Con el objetivo de combinar las ventajas de ambos enfoques, se implementó una estrategia de búsqueda híbrida. Para ello, se ejecutan en paralelo dos recuperadores: un recuperador léxico basado en LMIR y un recuperador denso basado en embeddings. Posteriormente, los resultados obtenidos por ambos sistemas se fusionan mediante el método Reciprocal Rank Fusion (RRF).

La puntuación final de cada documento se calcula según la siguiente expresión:

$$
\text{RRF}(d) = \sum_{r \in {\text{sparse}, \text{dense}}} \frac{1}{k + \text{rank}_r(d)}
$$

donde:

- $\text{rank}_r(d)$ representa la posición (1-based) del documento $d$ en la lista generada por el recuperador $r$. 
- $k$ es una constante de suavizado. En este trabajo se emplea $k = 60$, valor que reduce la diferencia entre posiciones consecutivas y evita que los primeros resultados dominen excesivamente la puntuación final.

La elección de RRF se fundamenta en que las puntuaciones producidas por ambos recuperadores no son directamente comparables. Mientras que el modelo LMIR genera puntuaciones basadas en probabilidades, el recuperador denso utiliza medidas derivadas de la similitud entre vectores. Una combinación directa de estas puntuaciones requeriría procesos de normalización adicionales que podrían introducir ruido en el sistema.

RRF evita este problema al utilizar únicamente la posición relativa de los documentos dentro de cada ranking. Además, favorece aquellos documentos que aparecen bien posicionados en ambos recuperadores, incrementando la confianza en su relevancia. 

## Re‑ranking con cross‑encoder

Tras obtener la lista inicial de documentos ordenada según la puntuación resultante de la fusión híbrida (rrf_score), se filtran los **primeros K resultados** que serán los candidatos para el análisis posterior. El sistema aplica una etapa adicional de re-ranking sobre ese subconjunto utilizando un modelo cross-encoder.

A diferencia de los bi-encoders empleados durante la recuperación densa, que generan representaciones vectoriales independientes para la consulta y los documentos, un cross-encoder procesa ambos textos conjuntamente en una única pasada por la red neuronal. Este enfoque permite modelar de forma explícita las interacciones entre los términos de la consulta y el contenido del documento, proporcionando una estimación de relevancia más precisa.

Debido a que el modelo debe evaluar cada par consulta-documento de manera individual, su coste computacional es considerablemente mayor que el de los métodos de recuperación utilizados en etapas anteriores. Por este motivo, el re-ranking se aplica únicamente sobre el conjunto reducido de documentos previamente recuperados, refinando el orden de los resultados sin afectar significativamente al tiempo total de respuesta.

En este proyecto empleamos el modelo **`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`**. Se trata de una versión multilingüe del conocido miniLM-v2, entrenada sobre el conjunto de datos MS MARCO traducido a 14 idiomas, incluido el español. Su tamaño reducido (12 capas, 384 dimensiones) y su buen rendimiento en tareas de re‑ranking de documentos lo convierten en una opción equilibrada entre precisión y eficiencia computacional.

## Posicionamiento final de los resultados

La relevancia obtenida durante las etapas de recuperación y re-ranking constituye un criterio fundamental para ordenar los documentos. Sin embargo, en un sistema orientado al dominio de las noticias, otros factores también influyen en la calidad de los resultados presentados al usuario. Entre ellos destacan la frescura de la información y la personalización basada en los intereses del usuario.

Con el objetivo de incorporar estos criterios al proceso de ordenación, el sistema calcula una puntuación final (`final_score`) mediante una combinación lineal ponderada de los distintos factores considerados:

$$
\text{final\_score} = w_{rel} \cdot \text{relevance\_score} + w_{per} \cdot \text{personalization\_score} + w_{rec} \cdot \text{recency\_factor}
$$

donde:

- `relevance_score` representa la relevancia del documento respecto a la consulta. Dependiendo de la configuración del sistema, esta puntuación puede corresponder al valor obtenido mediante Reciprocal Rank Fusion (RRF) o al score generado por el cross-encoder durante la fase de re-ranking.
- `personalization_similarity` mide la similitud entre el documento y el perfil de intereses del usuario.
- `recency_factor` cuantifica la frescura temporal del documento, favoreciendo las noticias más recientes.

Los pesos $(w_{rel}), (w_{per})$ y $(w_{rec})$ son configurables mediante el archivo .env y deben satisfacer la restricción:

$$
w_{rel} + w_{per} + w_{rec} = 1
$$

En las siguientes secciones se describe el procedimiento utilizado para calcular cada uno de estos factores.

### Factor de frescura (recency_factor)

El factor de frescura se utiliza para cuantificar la actualidad de cada documento dentro del sistema. Este componente asigna mayor peso a las publicaciones recientes y reduce progresivamente la contribución de aquellas más antiguas.

Su cálculo se basa en una función de decaimiento exponencial definida como:

$$
\text{recency\_factor}
=
e^{-\frac{\text{days\_ago}}{\text{decay\_days}}}
$$

donde:

- `days_ago` corresponde al número de días transcurridos desde la fecha de publicación del documento respecto al momento actual.
- `decay_days` es un hiperparámetro que controla la velocidad de disminución del factor. En este trabajo se fija en 30 días.

Este enfoque produce valores acotados en el intervalo:

$$
\text{recency\_factor} \in (0, 1]
$$

donde el valor máximo 1 se obtiene para documentos publicados en la fecha actual, y los valores decrecen de forma continua conforme aumenta la antigüedad.

En términos de implementación, cuando la fecha de publicación no puede ser interpretada correctamente o no está disponible, se asigna un valor neutro de 0.5. Asimismo, en caso de detectar inconsistencias temporales (por ejemplo, fechas futuras), se asigna directamente el valor máximo de 1.0.

### Factor de personalización (personalization_score)

El factor de personalización ajusta la relevancia de los documentos en función de los intereses del usuario, representados mediante un vector de perfil semántico. Se calcula la similitud coseno entre el perfil del usuario y el embedding del documento:

$$
\text{personalization\_similarity}(d) = \frac{\mathbf{p} \cdot \mathbf{e}_d}{\|\mathbf{p}\| \, \|\mathbf{e}_d\|}
$$

donde:

- $\mathbf{p}$ representa el vector de perfil del usuario
- $\mathbf{e}_d$ representa el embedding del documento

El valor resultante está acotado en el intervalo $[-1, 1]$. Posteriormente, este valor se normaliza mediante min‑max sobre el conjunto de resultados de la consulta, transformándolo a un `personalization_score` en $[0,1]$. En ausencia de historial suficiente (usuario nuevo o perfil no disponible), el sistema asigna un valor neutro de 0.

## Normalización de relevancia y personalización (min-max)

Las puntuaciones de relevancia obtenidas tras la fusión híbrida (RRF) o mediante el cross-encoder no se encuentran acotadas en un rango fijo y, por tanto, no son directamente comparables con el resto de factores del modelo de ranking. Para homogeneizar estas escalas y permitir una combinación lineal coherente, se aplica una normalización min-max sobre el conjunto de documentos recuperados en cada consulta.

Dada una puntuación original $s(d)$, la transformación a `relevance_score` se define como:

$$
\text{relevance\_score}(d)
=
\frac{s(d) - \min_{d' \in R} s(d')}
{\max_{d' \in R} s(d') - \min_{d' \in R} s(d')}
$$

donde $R$ representa el conjunto de documentos candidatos tras la fase de recuperación. Este procedimiento garantiza que las puntuaciones resultantes queden acotadas en el intervalo $[0,1]$.

En el caso particular en el que todos los documentos presentan la misma puntuación $(max = min)$, no es posible aplicar la normalización estándar. En esta situación degenerada, se asigna un valor por defecto constante (`default_value = 0.5`) a todos los documentos, evitando así la división por cero y manteniendo una escala neutra en ausencia de variabilidad.

## Configuración

Todas las variables relevantes se definen en el archivo `.env`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `RRF_K` | Constante de suavizado para RRF | `60` |
| `W_RELEVANCE` | Peso de la relevancia normalizada | `0.5` |
| `W_PERSONALIZATION` | Peso de la personalización | `0.25` |
| `W_RECENCY` | Peso de la actualidad | `0.25` |
| `RECENCY_DECAY_DAYS` | Días de decaimiento de la frescura | `30` |
| `CROSS_ENCODER_MODEL_NAME_OR_PATH` | Modelo cross‑encoder | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` |
| `ACTIVATE_CROSS_ENCODER_FOR_RELEVANCE` | Si es `true`, aplica re_ranking con cross encoder | `true` |

Estos valores se leen a través de `Settings` y se inyectan en `RankingContainer` desde `ConfigContainer`.

## Ventajas

- **Modularidad**: cada factor de ranking es independiente y fácil de añadir/quitar.
- **Configuración externa**: todos los pesos y parámetros se modifican desde `.env` sin tocar código.
- **Explicabilidad**: los campos intermedios (`relevance_score`, `personalization_score`, `recency_factor`) se devuelven en la API, permitiendo depurar el orden final.
- **Eficiencia**: las estrategias de scoring se ejecutan solo una vez por consulta, y el cross‑encoder solo sobre un subconjunto reducido.

## Limitaciones

- **Personalización por usuario**: requiere que el perfil de usuario esté precalculado (depende del módulo de recomendación). Si no hay historial, la personalización no influye.
- **Frescura dependiente de fechas**: si los documentos carecen de fecha válida, se asigna un valor neutro (0.5).
- **Cross‑encoder costoso**: aunque se aplica solo a un top N, su ejecución añade latencia.
