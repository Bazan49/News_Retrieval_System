from groq import AsyncGroq
from ..Domain.generator import BaseGenerator

class GroqGenerator(BaseGenerator):
    def __init__(
        self,
        api_key: str, 
        model_id: str = "llama-3.3-70b-versatile",
        temperature: float = 0.3,
        max_tokens: int = 700,
        frequency_penalty: float = 0.5,
        presence_penalty: float = 0.3,
        top_p: float = 0.95,
    ):
        self.client = AsyncGroq(api_key=api_key)
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.top_p = top_p

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                top_p=self.top_p,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error en Groq API: {e}")
            return "Lo siento, no pude generar una respuesta en este momento."