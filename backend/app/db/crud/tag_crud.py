from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import typing as t

from app.db import models, schemas

def get_tag(db: Session, tag_id: int) -> models.Tag:
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

def get_tag_by_name(db: Session, name: str) -> t.Optional[models.Tag]:
    # Returns an ORM instance or None
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def get_tags(db: Session, skip: int = 0, limit: int = 100) -> t.List[models.Tag]:
    # Returns a list of ORM Tag instances
    return db.query(models.Tag).offset(skip).limit(limit).all()

def get_tags_by_id_list(db: Session, tag_id_list: t.List[int]) -> t.List[models.Tag]:
    # Returns a list of ORM Tag instances
    return db.query(models.Tag).filter(models.Tag.id.in_(tag_id_list)).all()

def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    db_tag = models.Tag(
        name=tag.name,
        description=tag.description,
        is_active=tag.is_active,
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, tag_id: int) -> models.Tag:
    tag = get_tag(db, tag_id)  # ORM instance
    if not tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return tag

def edit_tag(db: Session, tag_id: int, tag: schemas.TagEdit) -> models.Tag:
    db_tag = get_tag(db, tag_id)  # ORM instance
    if not db_tag:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tag not found")

    update_data = tag.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag, key, value)

    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag
