from fastapi import APIRouter, HTTPException, status
from app.services.members_service import get_all_members

router = APIRouter()

@router.get("/")
async def list_members():
    try:
        members = await get_all_members()
        return {"data": members}
    except HTTPException as he:
        # Si el servicio ya levantó un HTTPException, la reenviamos
        raise he
    except Exception as e:
        # Cualquier error desconocido
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los miembros: {str(e)}"
        )
