from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base

class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    documents = relationship("DocumentTags", back_populates="tag")