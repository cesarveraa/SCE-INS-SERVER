# app/services/content_service.py

import os
import httpx
from app.dto.content_dto import ContentDTO
from app.models.content_model import ContentEntity
from fastapi import HTTPException, status
from app.utils.httpx_error_handler import handle_httpx_exception
from dotenv import load_dotenv
load_dotenv()

POCKETBASE_URL = os.getenv("POCKETBASE_URL")
ADMIN_EMAIL = os.getenv("POCKETBASE_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")

async def get_contents_by_chapter_id(chapter_id: int):
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

            # Buscar contenidos del capítulo
            res = await client.get(
                f"{POCKETBASE_URL}/api/collections/cap_contenido/records"
                f"?filter=(capitulos_id='{chapter_id}')&expand=contenido_id",
                headers=headers
            )
            res.raise_for_status()
            items = res.json().get("items", [])

            contents = []

            for item in items:
                contenido = item.get("expand", {}).get("contenido_id")
                if isinstance(contenido, list) and contenido:
                    contenido = contenido[0]

                if contenido:
                    entity = ContentEntity(
                        id=contenido["id"],
                        subtitulo=contenido.get("subtitulo"),
                        descripcion=contenido.get("descripcion"),
                        imagen=contenido.get("imagen"),
                        orden=contenido.get("orden")
                    )
                    contents.append(ContentDTO.from_entity(entity))

            return contents

    except Exception as e:
        raise handle_httpx_exception(e)
