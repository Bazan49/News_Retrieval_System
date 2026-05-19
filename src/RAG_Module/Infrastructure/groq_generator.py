from typing import List
from groq import AsyncGroq
from dotenv import load_dotenv
from ..Domain.generator import BaseGenerator
from src.Common.RetrievalResult.retrieval_result import RetrievalResult

load_dotenv() # Carga las variables de entorno de tu archivo .env

class GroqGenerator(BaseGenerator):
    def __init__(self, model_id: str = "llama-3.3-70b-versatile"):
        """
        Inicializa el generador de Groq.
        Args:
            model_id: El identificador del modelo a usar (ej. 'llama-3.3-70b-versatile',
                      'llama-3.1-8b-instant', 'mixtral-8x7b-32768').
        """
        # El SDK de Groq buscará automáticamente la variable GROQ_API_KEY
        self.client = AsyncGroq()
        self.model_id = model_id

    async def generate(self, query: str, documents: List[RetrievalResult]) -> str:
        """
        Genera una respuesta usando el modelo de Groq.
        """
        # --- Construcción del prompt y contexto (similar a lo que ya tienes) ---
        context = "\n".join([
            f"- Título: {doc.title}, Fuente: {doc.source}: {doc.snippet}"
            for doc in documents[:5]  # Limitamos a los 5 documentos más relevantes
        ])
        system_prompt = (
            "Eres un asistente experto en noticias. Tu tarea es responder preguntas del usuario "
            "basándote en los artículos proporcionados. Debes ser claro, conciso y útil. "
            "Si la información es suficiente, ofrece una respuesta completa y bien redactada. "
            "Si falta algún detalle, indícalo de forma natural (ej. 'Los artículos mencionan X, pero no especifican Y'). "
            "Evita frases como 'no se proporciona información' o 'según el contexto'. En su lugar, integra las fuentes de forma orgánica. "
            "Responde siempre en español, con un tono cercano y profesional."
        )
        user_prompt = f"Contexto de los artículos:\n{context}\n\nPregunta del usuario: {query}\n\nRespuesta:"

        # --- Llamada asíncrona a Groq ---
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,      # Controla la "creatividad" (0 = más factual, 1 = más creativo)
                max_tokens=700,       # Límite de longitud de la respuesta
                frequency_penalty=0.5,
                presence_penalty=0.3,
                top_p=0.95
            )
            # Extraemos y devolvemos la respuesta generada
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error en la llamada a Groq API: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."