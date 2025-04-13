# app/middleware/correlation.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from uuid import uuid4
from typing import Callable

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware que gestiona un Correlation ID para cada solicitud.
    Si la solicitud no incluye el header 'X-Correlation-ID', se genera uno nuevo.
    Este ID se añade al objeto request.state y a la respuesta.
    """
    
    async def dispatch(self, request, call_next: Callable):
        # Buscar header 'X-Correlation-ID'
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid4())
        # Guardar el correlation ID en el state para ser usado internamente (por ejemplo, para logs)
        request.state.correlation_id = correlation_id
        
        # Procesar la solicitud
        response = await call_next(request)
        # Añadir el correlation ID a la respuesta
        response.headers["X-Correlation-ID"] = correlation_id
        return response
