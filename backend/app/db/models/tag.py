from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.models.document_tags import document_tags

from app.db.session import Base

class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    description = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    documents = relationship("Document", secondary=document_tags, back_populates="tags")

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name