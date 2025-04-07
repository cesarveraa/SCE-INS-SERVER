# app/dto/content_dto.py

from pydantic import BaseModel
from typing import Optional
from app.models.content_model import ContentEntity

class ContentDTO(BaseModel):
    id: str
    subtitulo: Optional[str]
    descripcion: Optional[str]
    imagen: Optional[str]
    orden: Optional[int]

    @classmethod
    def from_entity(cls, entity: ContentEntity):
        return cls(**entity.dict())