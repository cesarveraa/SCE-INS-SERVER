# app/services/members_service.py

import os
import httpx
from fastapi import HTTPException, status

POCKETBASE_URL = os.getenv("POCKETBASE_URL")
ADMIN_EMAIL = os.getenv("POCKETBASE_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")

async def _admin_auth_client(client: httpx.AsyncClient) -> dict:
    """
    Autentica como administrador y retorna el header con token.
    """
    auth_response = await client.post(
        f"{POCKETBASE_URL}/api/admins/auth-with-password",
        json={"identity": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    auth_response.raise_for_status()
    admin_token = auth_response.json().get("token")
    return {"Authorization": f"Bearer {admin_token}"}

async def get_all_members():
    """
    Obtiene todos los usuarios (miembros) y sus relaciones.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = await _admin_auth_client(client)

            # Obtener todos los usuarios expandiendo el rol
            res_users = await client.get(
                f"{POCKETBASE_URL}/api/collections/usuario/records?expand=rol",
                headers=headers
            )
            res_users.raise_for_status()
            data_users = res_users.json()
            users_items = data_users.get("items", [])

            final_data = []

            for user in users_items:
                user_id = user.get("id")
                nombres = user.get("nombres", "")
                apellidos = user.get("apellidos", "")

                # Extraer el rol expandido
                rol_expanded = user.get("expand", {}).get("rol")
                if isinstance(rol_expanded, list) and rol_expanded:
                    rol_expanded = rol_expanded[0]
                rol_name = rol_expanded.get("rol", "Miembro") if rol_expanded else "Miembro"

                # Extraer año de ingreso a partir del campo 'semestre_ingreso'
                semestre = user.get("semestre_ingreso", "")
                anio_ingreso = semestre.split("-")[-1] if "-" in semestre else semestre

                # Consultar la colección intermedia 'usuario_capitulo' para obtener el capítulo
                url_user_caps = (
                    f"{POCKETBASE_URL}/api/collections/usuario_capitulo/records"
                    f"?filter=(usuario='{user_id}')&expand=capitulo"
                )
                res_caps = await client.get(url_user_caps, headers=headers)
                res_caps.raise_for_status()
                data_caps = res_caps.json()
                cap_items = data_caps.get("items", [])

                capitulo_name = "N/A"
                if cap_items:
                    first_rel = cap_items[0]
                    cap_expanded = first_rel.get("expand", {}).get("capitulo")
                    if isinstance(cap_expanded, list) and cap_expanded:
                        cap_expanded = cap_expanded[0]
                    capitulo_name = cap_expanded.get("capitulo", "N/A") if cap_expanded else "N/A"

                # Construir las iniciales a partir de nombres y apellidos
                initials = ""
                if nombres:
                    initials += nombres[0].upper()
                if apellidos:
                    initials += apellidos[0].upper()
                full_name = f"{nombres} {apellidos}".strip()

                member_info = {
                    "perfil": initials or "NA",
                    "nombre": full_name,
                    "rol": rol_name,
                    "capitulo": capitulo_name,
                    "anio_ingreso": anio_ingreso
                }
                final_data.append(member_info)

            return final_data

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con PocketBase"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Tiempo de espera agotado al consultar PocketBase"
        )
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"Error al consultar PocketBase: {http_err.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

async def create_member(member_data: dict):
    """
    Crea un miembro en PocketBase.
    `member_data` debe tener la información necesaria (p.ej.: nombres, apellidos, semestre_ingreso, etc.)
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = await _admin_auth_client(client)
            res = await client.post(
                f"{POCKETBASE_URL}/api/collections/usuario/records",
                json=member_data,
                headers=headers
            )
            res.raise_for_status()
            return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando el miembro: {str(e)}"
        )

async def update_member(member_id: str, member_data: dict):
    """
    Actualiza la información de un miembro en PocketBase.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = await _admin_auth_client(client)
            res = await client.patch(
                f"{POCKETBASE_URL}/api/collections/usuario/records/{member_id}",
                json=member_data,
                headers=headers
            )
            res.raise_for_status()
            return res.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando el miembro: {str(e)}"
        )

async def delete_member(member_id: str):
    """
    Elimina un miembro en PocketBase.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = await _admin_auth_client(client)
            res = await client.delete(
                f"{POCKETBASE_URL}/api/collections/usuario/records/{member_id}",
                headers=headers
            )
            res.raise_for_status()
            return {"detail": "Miembro eliminado"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando el miembro: {str(e)}"
        )
