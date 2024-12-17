from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.models.document_tags import document_tags

from app.db.session import Base

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    document_type = Column(String, index=True)
    file_weight = Column(Integer, index=True)
    pages = Column(Integer, index=True)
    s3_url = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="documents")
    tags = relationship("Tag", secondary=document_tags, back_populates="documents")    
    uploaded_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    is_up_to_date = Column(Boolean, default=True)