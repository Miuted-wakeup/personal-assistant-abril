import os
import sys

# agrega backend al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger
from backend.config import DISCORD_TOKEN

logger = setup_logger("DiscordBot")

def run_bot():
    # inicia bot de discord
    logger.info("iniciando bot discord")
    if not DISCORD_TOKEN:
        logger.error("falta token de discord")
        return
    
if __name__ == "__main__":
    run_bot()
