import os
import requests
from backend.logger import setup_logger
from backend.config import BRAVE_SEARCH_API_KEY

logger = setup_logger("WebSearch")

class BraveSearch:
    def __init__(self):
        self.api_url = "https://api.search.brave.com/res/v1/web/search"
        self.api_key = BRAVE_SEARCH_API_KEY
        
        if not self.api_key or self.api_key == "ingresa_tu_api_key_de_brave_aqui":
            logger.warning("BRAVE_SEARCH_API_KEY no configurada en .env")

    def search(self, query, max_results=5):
        if not query:
            return "No especificaste qué buscar"
            
        if not self.api_key or self.api_key == "ingresa_tu_api_key_de_brave_aqui":
            return "Error: No tengo acceso a internet porque falta mi llave de Brave Search."
            
        logger.info(f"buscando en internet: '{query}'")
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": max_results,
            "search_lang": "es"
        }
        
        try:
            response = requests.get(self.api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 401:
                return "Error: API key de Brave inválida o expirada."
            if response.status_code != 200:
                return f"Error en búsqueda: {response.status_code}"
                
            data = response.json()
            web_results = data.get("web", {}).get("results", [])
            
            if not web_results:
                return "No encontré información sobre eso en internet."
                
            summary_parts = []
            for res in web_results[:max_results]:
                content = res.get("description", "")
                if content:
                    summary_parts.append(content.strip())
            
            return " ".join(summary_parts) if summary_parts else "Encontré enlaces pero sin descripción útil."
            
        except Exception as e:
            logger.error(f"error en búsqueda: {e}")
            return "Hubo un error de conexión al buscar en internet."

# Instancia global
brave_search = BraveSearch()

def buscar_en_internet(query):
    """Función que será llamada por el LLM"""
    return brave_search.search(query)
