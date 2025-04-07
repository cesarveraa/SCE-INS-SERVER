# app/services/chapters_service.py

import os
import httpx
from fastapi import HTTPException, status
from app.models.chapters_model import ChapterEntity
from app.dto.chapter_dto import ChapterDTO
from app.utils.httpx_error_handler import handle_httpx_exception
from dotenv import load_dotenv
load_dotenv()

POCKETBASE_URL = os.getenv("POCKETBASE_URL")
ADMIN_EMAIL = os.getenv("POCKETBASE_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")

async def get_all_chapters():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Autenticación
            auth_response = await client.post(
                f"{POCKETBASE_URL}/api/admins/auth-with-password",
                json={"identity": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
            )
            auth_response.raise_for_status()
            token = auth_response.json().get("token")
            headers = {"Authorization": f"Admin {token}"}

            # Obtener capítulos con usuario expandido
            res = await client.get(
                f"{POCKETBASE_URL}/api/collections/chaptesr/records?expand=usuario_id",
                headers=headers
            )
            res.raise_for_status()
            items = res.json().get("items", [])

            chapters = []

            for item in items:
                # Datos del usuario (expandido)
                usuario = item.get("expand", {}).get("usuario_id")
                if isinstance(usuario, list) and usuario:
                    usuario = usuario[0]

                nombres = usuario.get("nombres", "") if usuario else ""
                apellidos = usuario.get("apellidos", "") if usuario else ""
                usuario_nombre = f"{nombres} {apellidos}".strip() or None

                # Crear entidad y DTO
                entity = ChapterEntity(
                    id=item["id"],
                    nombre=item.get("nombre"),
                    descripcion=item.get("descripcion"),
                    usuario_id=item.get("usuario_id"),
                )

                dto = ChapterDTO.from_entity(entity, usuario_nombre=usuario_nombre)
                chapters.append(dto)

            return chapters

    except Exception as e:
        raise handle_httpx_exception(e)
