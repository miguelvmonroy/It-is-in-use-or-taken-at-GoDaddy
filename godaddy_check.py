# godaddy_check.py
import os, sys, requests
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env con tus credenciales

API_KEY    = os.getenv("GODADDY_API_KEY")
API_SECRET = os.getenv("GODADDY_API_SECRET")
BASE_URL   = "https://api.ote-godaddy.com/v1"

if not (API_KEY and API_SECRET):
    sys.exit("❌  Faltan GODADDY_API_KEY y/o GODADDY_API_SECRET en el entorno")

def is_available(domain: str) -> bool:
    """Devuelve True si el dominio está libre en GoDaddy."""
    endpoint = f"{BASE_URL}/domains/available"
    headers  = {
        "Authorization": f"sso-key {API_KEY}:{API_SECRET}",
        "Accept": "application/json"
    }
    resp = requests.get(endpoint, params={"domain": domain}, headers=headers, timeout=10)
    resp.raise_for_status()     # lanza excepción si algo salió mal
    return resp.json()["available"]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python godaddy_check.py ejemplo.com")
        sys.exit(1)

    dominio = sys.argv[1].lower()
    try:
        libre = is_available(dominio)
        print(f"✅  {dominio} está DISPONIBLE" if libre else f"🚫  {dominio} ya está tomado")
    except requests.HTTPError as e:
        print("💥  Error al consultar GoDaddy:", e)
