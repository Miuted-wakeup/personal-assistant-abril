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
            return "No especificaste que buscar"
            
        if not self.api_key or self.api_key == "ingresa_tu_api_key_de_brave_aqui":
            return "Error: No tengo acceso a internet porque falta mi llave de Brave Search."
            
        logger.info(f"Buscando en Brave Search: '{query}'")
        
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
                logger.error("API key de Brave invalida o expirada.")
                return "Error: API key de Brave invalida o expirada."
            if response.status_code != 200:
                logger.error(f"Error HTTP {response.status_code} en Brave Search")
                return f"Error en busqueda: {response.status_code}"
                
            data = response.json()
            web_results = data.get("web", {}).get("results", [])
            
            if not web_results:
                logger.info(f"Brave Search no encontro resultados para '{query}'")
                return "No encontre informacion sobre eso en internet."
                
            logger.info(f"Brave Search retorno {len(web_results)} resultados:")
            summary_parts = []
            for i, res in enumerate(web_results[:max_results]):
                title = res.get("title", "Sin titulo")
                desc = res.get("description", "")
                url = res.get("url", "")
                logger.info(f"  [{i+1}] {title} ({url[:45]}...) -> {desc[:80]}...")
                if desc:
                    summary_parts.append(f"Fuente ({title}): {desc.strip()}")
            
            resumen_final = " ".join(summary_parts) if summary_parts else "Se encontraron enlaces sin descripcion util."
            logger.debug(f"Contenido final sintetizado para LLM ({len(resumen_final)} caracteres)")
            return resumen_final
            
        except Exception as e:
            logger.error(f"Error de conexion en busqueda: {e}")
            return "Hubo un error de conexion al buscar en internet."

# Instancia global
brave_search = BraveSearch()

def buscar_en_internet(query):
    # Funcion invocada por el Function Calling del LLM
    return brave_search.search(query)
