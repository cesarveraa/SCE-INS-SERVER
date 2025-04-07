# app/dto/chapter_dto.py

from pydantic import BaseModel
from typing import Optional
from app.models.chapters_model import ChapterEntity

class ChapterDTO(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    usuario_id: Optional[str]
    usuario_nombre: Optional[str]

    @classmethod
    def from_entity(cls, entity: ChapterEntity, usuario_nombre: Optional[str] = None):
        data = entity.dict()
        data["usuario_nombre"] = usuario_nombre
        return cls(**data)
