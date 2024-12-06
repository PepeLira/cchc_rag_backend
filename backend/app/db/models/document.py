from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.models_group import Base

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
    user = relationship("User", back_populates="document")
    tags = relationship("DocumentTags", back_populates="document")