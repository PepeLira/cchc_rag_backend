from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import PickleType

Base = declarative_base()

# Association table for Document <--> Tag (Many-to-many)
document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_hash = Column(String, index=True, unique=True)
    title = Column(String, unique=True, nullable=False)

    doc_path = Column(String, nullable=False)
    output_dir = Column(String, nullable=False)
    markdown_path = Column(String, nullable=True)
    images_path = Column(String, nullable=True)

    page_count = Column(Integer, nullable=True)

    # a boolean to indicate if the document is on the server
    is_uploaded = Column(Integer, nullable=False, default=0)
    
    # a boolean to indicate if the document is an update to an existing document
    local_update = Column(Integer, nullable=False, default=0)

    # One-to-many: Document -> Chunk
    chunks = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan"
    )

    # Many-to-many: Document -> Tag
    tags = relationship("Tag", secondary=document_tags, back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(PickleType, nullable=True)
    page_number = Column(Integer, nullable=True)

    # Relationship back to Document
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id})>"

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # Many-to-many: Tag -> Document
    documents = relationship("Document", secondary=document_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
