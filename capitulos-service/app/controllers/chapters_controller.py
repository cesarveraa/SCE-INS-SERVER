# app/controllers/chapters_controller.py

from fastapi import APIRouter, Path
from typing import List
from app.services.chapters_service import get_all_chapters
from app.services.content_service import get_contents_by_chapter_id
from app.dto.chapter_dto import ChapterDTO
from app.dto.content_dto import ContentDTO

router = APIRouter()

@router.get("/", response_model=List[ChapterDTO], summary="Lista todos los capitulos")
async def list_chapters():
    return await get_all_chapters()

@router.get("/{chapter_id}/contents", response_model=List[ContentDTO], summary="Contenidos de un capítulo")
async def list_chapter_contents(chapter_id: str = Path(..., gt=0)):
    return await get_contents_by_chapter_id(chapter_id)
