from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.controllers.chapters_controller import router as chapters_router
from app.middleware.middleware import setup_middlewares
from app.utils.exception_handler import setup_exception_handlers
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Servicio de Capitulos",
    description="Microservicio para obtener los capitulos desde PocketBase.",
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

# Middlewares and Exception Handlers
setup_middlewares(app)
setup_exception_handlers(app)

# Rutas
app.include_router(chapters_router, prefix="/chapters", tags=["Capitulos"])

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Monitoreo"])
async def health_check():
    return {"status": "ok", "service": "chapters-service"}