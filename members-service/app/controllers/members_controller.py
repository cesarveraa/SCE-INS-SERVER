# app/controllers/members_controller.py
from fastapi import APIRouter, HTTPException, status, Body
from app.services.members_service import (
    get_all_members, create_member, update_member, delete_member
)

router = APIRouter()

# GET: Listar miembros (público)
@router.get("/")
async def list_members():
    try:
        members = await get_all_members()
        return {"data": members}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los miembros: {str(e)}"
        )

# POST: Crear un nuevo miembro (endpoint privado)
@router.post("/", include_in_schema=False)
async def add_member(member_data: dict = Body(...)):
    try:
        result = await create_member(member_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el miembro: {str(e)}"
        )

# PATCH: Actualizar un miembro (endpoint privado)
@router.patch("/{member_id}", include_in_schema=False)
async def modify_member(member_id: str, member_data: dict = Body(...)):
    try:
        result = await update_member(member_id, member_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el miembro: {str(e)}"
        )

# DELETE: Eliminar un miembro (endpoint privado)
@router.delete("/{member_id}", include_in_schema=False)
async def remove_member(member_id: str):
    try:
        result = await delete_member(member_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el miembro: {str(e)}"
        )
