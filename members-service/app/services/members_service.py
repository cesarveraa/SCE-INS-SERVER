import os
import httpx
from fastapi import HTTPException, status

POCKETBASE_URL = os.getenv("POCKETBASE_URL")
ADMIN_EMAIL = os.getenv("POCKETBASE_ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")

async def get_all_members():
    """
    Autentica como administrador y obtiene todos los registros de la colección 'usuario'
    junto con la relación de rol y, a partir de la tabla intermedia 'usuario_capitulo',
    obtiene el nombre del capítulo. Retorna una lista de objetos con la siguiente información:
    - perfil (iniciales)
    - nombre (nombre completo)
    - rol
    - capitulo (nombre del capítulo)
    - anio_ingreso (extraído del campo 'semestre_ingreso')
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Autenticación de administrador (ahora enviando 'identity')
            auth_response = await client.post(
                f"{POCKETBASE_URL}/api/admins/auth-with-password",
                json={"identity": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
            )
            auth_response.raise_for_status()
            admin_token = auth_response.json().get("token")
            headers = {"Authorization": f"Admin {admin_token}"}
            
            # 2. Obtener todos los usuarios expandiendo el rol
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

                # 3. Consultar la colección intermedia 'usuario_capitulo' para obtener el capítulo
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
                    # Ajusta la clave según el nombre del campo en tu colección 'capitulo'
                    capitulo_name = cap_expanded.get("capitulo", "N/A") if cap_expanded else "N/A"

                # 4. Construir las iniciales a partir de nombres y apellidos
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
