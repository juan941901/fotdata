from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime


class SystemMessage(BaseModel):
    """Mensaje del sistema que define el comportamiento base del modelo."""
    content: str
    name: str
    description: Optional[str] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmbeddingRequest(BaseModel):
    """Request para generar embeddings de texto."""
    text: str
    model: Optional[str] = None


class EmbeddingResponse(BaseModel):
    """Response con el vector embedding generado."""
    embedding: List[float]
    model: str
    text: str
    text_hash: str


class StoredEmbedding(EmbeddingResponse):
    """Embedding almacenado con metadatos."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GeminiRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 512
    system_message_id: Optional[int] = None  # ID del mensaje del sistema a usar
    context_texts: Optional[List[str]] = None  # Textos relevantes del contexto


class GeminiResponse(BaseModel):
    text: str
    raw: Optional[Any] = None
    used_system_message: Optional[SystemMessage] = None
    used_context: Optional[List[str]] = None
