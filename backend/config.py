import os
import json
from dotenv import load_dotenv

# carga envs
load_dotenv()

# carga config json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"No config en: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# variables globales
settings = load_config()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
