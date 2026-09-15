import json
import httpx
from backend.logger import setup_logger

logger = setup_logger("HermesClient")

class HermesClient:
    def __init__(self, endpoint="http://127.0.0.1:8642/v1", api_key="hermes_local", model="hermes-agent", timeout=10.0):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def is_available(self) -> bool:
        """Comprueba de forma rapida si el gateway de Hermes Agent esta activo."""
        try:
            url = f"{self.endpoint}/models"
            resp = httpx.get(url, headers=self.headers, timeout=0.8)
            return resp.status_code in [200, 401, 403]
        except Exception:
            return False

    def generate_response(self, messages, max_tokens=300, temperature=0.7) -> str:
        """Envia la conversacion al gateway de Hermes Agent y obtiene la respuesta."""
        url = f"{self.endpoint}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            logger.info(f"[HermesClient] Enviando solicitud al gateway de Hermes en {url}...")
            resp = httpx.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                return content.strip()
            return ""
        except httpx.ConnectError:
            logger.warning("[HermesClient] No se pudo conectar al gateway de Hermes (Servicio no activo o fuera de linea).")
            raise
        except Exception as e:
            logger.error(f"[HermesClient] Error en comunicacion con Hermes: {e}")
            raise
