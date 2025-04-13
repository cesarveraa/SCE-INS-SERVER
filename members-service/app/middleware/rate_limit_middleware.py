# app/middleware/rate_limit_middleware.py

import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para limitar el número de solicitudes de cada cliente (por IP)
    en una ventana de tiempo específica. Si se excede el límite, se responde con
    un error 429 (Too Many Requests).
    """
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}  # Diccionario para llevar la cuenta: {ip: [timestamps]}
    
    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host  # Obtener la IP del cliente
        current_time = time.time()
        
        # Inicializa la lista de tiempos si la IP no está registrada
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Eliminar solicitudes que superan la ventana de tiempo
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if timestamp > current_time - self.window_seconds
        ]
        
        # Verificar si se excede el límite
        if len(self.clients[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Registrar la nueva solicitud
        self.clients[client_ip].append(current_time)
        
        # Procesar la solicitud
        response = await call_next(request)
        return response
