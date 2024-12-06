from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.models_group import Base

class DocumentTags(Base):
    __tablename__ = "document_tags"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('document.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))
    document = relationship("Document", back_populates="tags")
    tag = relationship("Tag", back_populates="documents")