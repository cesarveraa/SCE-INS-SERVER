# app/models/chapter_model.py

from pydantic import BaseModel
from typing import Optional

class ChapterEntity(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    usuario_id: Optional[str]
