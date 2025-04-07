# middleware.py

import logging
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi import FastAPI


# Logger para errores y eventos
logger = logging.getLogger("uvicorn.error")

def setup_middlewares(app: FastAPI):
    # 1. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Cambia esto en producción
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 3. Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Cámbialo a tu dominio en producción
    )

    # 4. Seguridad con headers
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
        security_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": csp,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        response.headers.update(security_headers)
        return response
