import httpx
import logging
from src.RAGModule.Domain.generator import BaseGenerator

logger = logging.getLogger(__name__)

class MistralGenerator(BaseGenerator):
    def __init__(
        self,
        api_key: str,
        model_id: str = "mistral-small-latest",
        temperature: float = 0.3,
        max_tokens: int = 500,
        frequency_penalty: float = 0.5,
        presence_penalty: float = 0.3,
        top_p: float = 0.95
    ):
        self.api_key = api_key
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.top_p = top_p
        self.base_url = "https://api.mistral.ai/v1"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_id,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "frequency_penalty": self.frequency_penalty,
                        "presence_penalty": self.presence_penalty,
                        "top_p": self.top_p,
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Mistral API HTTP error: {e.response.status_code} - {e.response.text}")
            return "Lo siento, la API de generación respondió con un error. Inténtalo de nuevo más tarde."
        except httpx.RequestError as e:
            logger.error(f"Mistral API request error: {str(e)}")
            return "Lo siento, no pude conectar con el servicio de generación. Verifica tu conexión."
        except Exception as e:
            logger.error(f"Unexpected error in MistralGenerator: {str(e)}")
            return "Lo siento, ocurrió un error inesperado al generar la respuesta."