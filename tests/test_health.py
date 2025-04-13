# tests/test_health.py
import requests

def test_health_endpoint():
    # En entornos de Docker Compose, usa el nombre del servicio FastAPI tal como aparece en la red interna.
    # Por ejemplo, si en docker-compose.yml definiste el servicio como "members-service"
    # o "fastapi_service", usa ese nombre. Aquí usaremos "members-service".
    url = "http://members-service:8000/health"
    response = requests.get(url)
    
    # Se espera un código 200
    assert response.status_code == 200, f"Endpoint health devolvió {response.status_code}"
    data = response.json()
    # Verifica el contenido (ajusta según lo implementado)
    assert data.get("status") == "ok", f"El status esperado era 'ok', pero se recibió: {data.get('status')}"
