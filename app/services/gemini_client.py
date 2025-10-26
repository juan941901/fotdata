from typing import Optional, Dict, Any, List
import json
import hashlib
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..core import config


class GeminiError(Exception):
    pass


class GeminiClient:
    """
    Cliente asíncrono para consumir el modelo Gemini.
    Soporta generación de texto con contexto y embeddings.
    """

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None, 
                 model: Optional[str] = None, embed_endpoint: Optional[str] = None,
                 embed_model: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.endpoint = endpoint or config.GEMINI_ENDPOINT
        self.model = model or config.GEMINI_MODEL
        self.embed_endpoint = embed_endpoint or config.GEMINI_EMBED_ENDPOINT
        self.embed_model = embed_model or config.GEMINI_EMBED_MODEL
        self._client = httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise GeminiError("GEMINI_API_KEY no está configurada")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)))
    async def generate_text(self, prompt: str, model: Optional[str] = None,
                          temperature: float = 0.2, max_tokens: int = 512,
                          system_message: Optional[str] = None,
                          context_texts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Genera texto usando el modelo, opcionalmente con mensaje del sistema y contexto."""
        model = model or self.model
        
        # Construye el prompt completo con sistema y contexto
        full_prompt = ""
        if system_message:
            full_prompt += f"System: {system_message}\n\n"
        if context_texts:
            full_prompt += "Context:\n" + "\n".join(context_texts) + "\n\n"
        full_prompt += f"User: {prompt}\n\nAssistant:"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "temperature": float(temperature),
            "max_output_tokens": int(max_tokens),
        }

        resp = await self._client.post(self.endpoint, headers=self._get_headers(), json=payload)

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise GeminiError(f"Gemini request failed: {e.response.status_code} - {detail}")

        try:
            return resp.json()
        except Exception:
            return {"text": resp.text}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)))
    async def generate_embedding(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Genera un embedding para el texto dado."""
        model = model or self.embed_model

        # Calcula hash del texto para identificación única
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        payload = {
            "model": model,
            "text": text,
        }

        resp = await self._client.post(
            self.embed_endpoint,
            headers=self._get_headers(),
            json=payload
        )

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            detail = None
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise GeminiError(f"Embedding generation failed: {e.response.status_code} - {detail}")

        try:
            response_data = resp.json()
            # Adapta según la estructura real de tu proveedor
            embedding = response_data.get("embedding", response_data.get("embeddings", []))
            return {
                "embedding": embedding,
                "model": model,
                "text": text,
                "text_hash": text_hash,
            }
        except Exception as e:
            raise GeminiError(f"Failed to parse embedding response: {e}")
