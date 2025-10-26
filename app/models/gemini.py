from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base


class SystemMessage(Base):
    """Modelo para almacenar mensajes del sistema que definen el comportamiento base."""
    __tablename__ = "system_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Embedding(Base):
    """Modelo para almacenar embeddings generados."""
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    text_hash = Column(String, unique=True, index=True)
    embedding = Column(JSON, nullable=False)  # Vector almacenado como JSON
    model = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())