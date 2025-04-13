# members-service/app/consul_registration.py
import os
import requests

CONSUL_ADDRESS = os.getenv("CONSUL_ADDRESS", "http://consul:8500")
SERVICE_NAME = "members-service"
# Por defecto, toma el HOSTNAME del contenedor como SERVICE_ID
SERVICE_ID = os.getenv("HOSTNAME", SERVICE_NAME)
SERVICE_ADDRESS = os.getenv("SERVICE_ADDRESS", "members_service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

def register_service():
    url = f"{CONSUL_ADDRESS}/v1/agent/service/register"
    payload = {
        "Name": SERVICE_NAME,
        "ID": SERVICE_ID,
        "Address": SERVICE_ADDRESS,
        "Port": SERVICE_PORT,
        "Check": {
            "HTTP": f"http://{SERVICE_ADDRESS}:{SERVICE_PORT}/health",
            "Interval": "10s"
        }
    }
    try:
        r = requests.put(url, json=payload)
        r.raise_for_status()
        print("Servicio registrado en Consul.")
    except Exception as e:
        print(f"Error al registrar el servicio en Consul: {e}")

def deregister_service():
    url = f"{CONSUL_ADDRESS}/v1/agent/service/deregister/{SERVICE_ID}"
    try:
        r = requests.put(url)
        r.raise_for_status()
        print("Servicio desregistrado en Consul.")
    except Exception as e:
        print(f"Error al desregistrar el servicio en Consul: {e}")
