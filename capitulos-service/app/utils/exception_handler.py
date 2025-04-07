import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

logger = logging.getLogger("uvicorn.error")

def setup_exception_handlers(app: FastAPI):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")

        # Personaliza respuestas comunes
        if exc.status_code == HTTP_404_NOT_FOUND:
            message = "El recurso solicitado no fue encontrado."
        elif exc.status_code == HTTP_405_METHOD_NOT_ALLOWED:
            message = "El método HTTP no está permitido para este endpoint."
        elif exc.status_code == HTTP_401_UNAUTHORIZED:
            message = "No autorizado. Por favor inicia sesión."
        elif exc.status_code == HTTP_403_FORBIDDEN:
            message = "Acceso prohibido. No tienes los permisos necesarios."
        else:
            message = exc.detail

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": message},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Error de validación en los datos enviados.", "detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Ocurrió un error inesperado en el servidor."},
        )
