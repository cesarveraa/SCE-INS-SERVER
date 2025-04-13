import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

# Importación de OpenTelemetry para Distributed Tracing
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.utils.consul_registration import register_service, deregister_service

# Importar los middlewares personalizados
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware

# Importa el router de members
from app.controllers.members_controller import router as members_router
# Importa la función para iniciar el tracer
from app.utils.tracing import init_tracer
app = FastAPI(
    title="Servicio de Miembros",
    description="Microservicio para listar (y CRUD) de miembros desde PocketBase.",
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
# 1. Inicializa el tracer
init_tracer()


# 3. Instrumenta la app con OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# 4. Registra el evento startup para registrar en consul
# y el shutdown para desregistrar

# Configuración del logger
logger = logging.getLogger("uvicorn.error")
@app.on_event("startup")
async def startup_event():
    register_service()

@app.on_event("shutdown")
async def shutdown_event():
    deregister_service()

# =========================================================
# 1. Inicializar Tracer con OpenTelemetry (para Distributed Tracing)
# =========================================================
def init_tracer():
    resource = Resource.create({"service.name": "members-service"})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "jaeger"),
        agent_port=int(os.getenv("JAEGER_PORT", "6831")),
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(span_processor)

init_tracer()

# =========================================================
# 2. Crear instancia de FastAPI
# =========================================================


# Instrumentar la app con OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# =========================================================
# 3. Configurar Middlewares Globales
# =========================================================
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Middleware personalizado de Correlation ID
app.add_middleware(CorrelationIdMiddleware)

# Middleware de Rate Limit para limitar solicitudes por IP
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Middleware de seguridad de headers
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
    headers_security = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": csp,
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    response.headers.update(headers_security)
    return response

# =========================================================
# 4. Manejadores de Excepciones Globales
# =========================================================
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# =========================================================
# 5. Registro del Router de Members
# =========================================================
app.include_router(members_router, prefix="/members", tags=["Miembros"])

# =========================================================
# 6. Endpoints de Control y Debug
# =========================================================
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Monitoreo"])
async def health_check():
    return {"status": "ok", "service": "members-service"}

