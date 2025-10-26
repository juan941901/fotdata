from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from . import models, schemas
from .core.security import get_password_hash


# --- User CRUD Operations ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- System Message CRUD Operations ---

def create_system_message(db: Session, message: schemas.SystemMessage) -> models.SystemMessage:
    db_message = models.SystemMessage(**message.model_dump(exclude={'created_at', 'updated_at'}))
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_system_message(db: Session, message_id: int) -> Optional[models.SystemMessage]:
    return db.query(models.SystemMessage).filter(models.SystemMessage.id == message_id).first()

def get_system_messages(db: Session, skip: int = 0, limit: int = 100) -> List[models.SystemMessage]:
    return db.query(models.SystemMessage).offset(skip).limit(limit).all()

def update_system_message(db: Session, message_id: int, message: schemas.SystemMessage) -> Optional[models.SystemMessage]:
    db_message = db.query(models.SystemMessage).filter(models.SystemMessage.id == message_id).first()
    if db_message:
        for key, value in message.model_dump(exclude={'created_at', 'updated_at'}).items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
    return db_message


# --- Embedding CRUD Operations ---

def create_embedding(db: Session, embedding: schemas.EmbeddingResponse) -> models.Embedding:
    db_embedding = models.Embedding(**embedding.model_dump())
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    return db_embedding

def get_embedding(db: Session, embedding_id: int) -> Optional[models.Embedding]:
    return db.query(models.Embedding).filter(models.Embedding.id == embedding_id).first()

def get_embedding_by_hash(db: Session, text_hash: str) -> Optional[models.Embedding]:
    return db.query(models.Embedding).filter(models.Embedding.text_hash == text_hash).first()

def get_embeddings(db: Session, skip: int = 0, limit: int = 100) -> List[models.Embedding]:
    return db.query(models.Embedding).order_by(desc(models.Embedding.created_at)).offset(skip).limit(limit).all()

def delete_embedding(db: Session, embedding_id: int) -> bool:
    db_embedding = db.query(models.Embedding).filter(models.Embedding.id == embedding_id).first()
    if db_embedding:
        db.delete(db_embedding)
        db.commit()
        return True
    return False
