from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    func
)

from sqlalchemy.orm import relationship

from app.config.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        String,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    stored_filename = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="processing"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id = Column(
        String,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    chunk_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    page_number = Column(
        Integer,
        nullable=False
    )

    text = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )