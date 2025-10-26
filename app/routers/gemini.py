from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from ..schemas.gemini import (
    GeminiRequest, GeminiResponse, SystemMessage,
    EmbeddingRequest, EmbeddingResponse, StoredEmbedding
)
from ..services.gemini_client import GeminiClient, GeminiError
from ..dependencies import get_gemini_client, get_db
from .. import crud

router = APIRouter()


# --- Text Generation Endpoints ---

@router.post("/generate", response_model=GeminiResponse)
async def generate(
    request: GeminiRequest,
    client: GeminiClient = Depends(get_gemini_client),
    db: Session = Depends(get_db)
):
    """Genera texto usando el modelo Gemini configurado."""
    try:
        # Obtener mensaje del sistema si se especifica
        system_message = None
        if request.system_message_id:
            db_message = crud.get_system_message(db, request.system_message_id)
            if not db_message:
                raise HTTPException(status_code=404, detail="System message not found")
            system_message = db_message.content

        # Genera el texto con el contexto completo
        resp = await client.generate_text(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_message=system_message,
            context_texts=request.context_texts
        )
    except GeminiError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    # Extraer texto de la respuesta
    text = None
    if isinstance(resp, dict):
        if "text" in resp and isinstance(resp["text"], str):
            text = resp["text"]
        elif "choices" in resp and isinstance(resp["choices"], list) and len(resp["choices"]) > 0:
            first = resp["choices"][0]
            if isinstance(first, dict) and "text" in first:
                text = first["text"]

    if text is None:
        text = str(resp)

    # Construir respuesta con contexto usado
    response = GeminiResponse(
        text=text,
        raw=resp,
        used_context=request.context_texts
    )
    
    if request.system_message_id:
        response.used_system_message = SystemMessage.from_orm(db_message)
    
    return response


# --- System Message Endpoints ---

@router.post("/system-messages", response_model=SystemMessage)
def create_system_message(
    message: SystemMessage,
    db: Session = Depends(get_db)
):
    """Crea un nuevo mensaje del sistema."""
    return crud.create_system_message(db, message)

@router.get("/system-messages", response_model=List[SystemMessage])
def list_system_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos los mensajes del sistema."""
    return crud.get_system_messages(db, skip=skip, limit=limit)

@router.get("/system-messages/{message_id}", response_model=SystemMessage)
def get_system_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un mensaje del sistema específico."""
    message = crud.get_system_message(db, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="System message not found")
    return message

@router.put("/system-messages/{message_id}", response_model=SystemMessage)
def update_system_message(
    message_id: int,
    message: SystemMessage,
    db: Session = Depends(get_db)
):
    """Actualiza un mensaje del sistema existente."""
    updated = crud.update_system_message(db, message_id, message)
    if updated is None:
        raise HTTPException(status_code=404, detail="System message not found")
    return updated


# --- Embedding Endpoints ---

@router.post("/embeddings", response_model=StoredEmbedding)
async def create_embedding(
    request: EmbeddingRequest,
    client: GeminiClient = Depends(get_gemini_client),
    db: Session = Depends(get_db)
):
    """Genera y almacena un embedding para el texto dado."""
    try:
        # Primero intentamos encontrar un embedding existente
        embedding_response = await client.generate_embedding(
            text=request.text,
            model=request.model
        )
        
        # Buscar si ya existe un embedding con el mismo hash
        existing = crud.get_embedding_by_hash(db, embedding_response["text_hash"])
        if existing:
            return StoredEmbedding.from_orm(existing)
        
        # Si no existe, crear nuevo
        return crud.create_embedding(db, EmbeddingResponse(**embedding_response))
        
    except GeminiError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

@router.get("/embeddings", response_model=List[StoredEmbedding])
def list_embeddings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos los embeddings almacenados."""
    return crud.get_embeddings(db, skip=skip, limit=limit)

@router.get("/embeddings/{embedding_id}", response_model=StoredEmbedding)
def get_embedding(
    embedding_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un embedding específico."""
    embedding = crud.get_embedding(db, embedding_id)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Embedding not found")
    return embedding

@router.delete("/embeddings/{embedding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_embedding(
    embedding_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un embedding almacenado."""
    if not crud.delete_embedding(db, embedding_id):
        raise HTTPException(status_code=404, detail="Embedding not found")
