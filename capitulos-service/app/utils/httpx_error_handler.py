# app/utils/httpx_error_handler.py

from fastapi import HTTPException, status
import httpx

def handle_httpx_exception(e: Exception) -> HTTPException:
    if isinstance(e, httpx.ConnectError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con PocketBase"
        )
    elif isinstance(e, httpx.TimeoutException):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Tiempo de espera agotado"
        )
    elif isinstance(e, httpx.HTTPStatusError):
        return HTTPException(
            status_code=e.response.status_code,
            detail=f"PocketBase error: {e.response.text}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
