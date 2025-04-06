import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

# Importa tu router
from app.controllers.members_controller import router as members_router

app = FastAPI(
    title="Servicio de Miembros",
    description="Microservicio para listar miembros desde PocketBase.",
    version="1.0.0",
    contact={
        "name": "Equipo de Soporte",
        "email": "soporte@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Logger para reportar errores u eventos importantes
logger = logging.getLogger("uvicorn.error")

# 1. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajusta según tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Middleware GZip (optimiza tamaño de respuestas)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Restricción de hosts (en producción, cámbialo a tu dominio)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 4. Middleware de seguridad de headers
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    # Actualizamos la política CSP para permitir recursos externos necesarios por Swagger UI
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

# 5. Manejo de errores global
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

# 6. Registro del router
app.include_router(members_router, prefix="/members", tags=["Miembros"])

# 7. Rutas de control / debug
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Monitoreo"])
async def health_check():
    return {"status": "ok", "service": "members-service"}
