# app/models/content_model.py

from pydantic import BaseModel
from typing import Optional

class ContentEntity(BaseModel):
    id: str
    subtitulo: Optional[str]
    descripcion: Optional[str]
    imagen: Optional[str]
    orden: Optional[int]
