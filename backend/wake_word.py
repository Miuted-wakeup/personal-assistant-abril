from backend.logger import setup_logger
from backend.config import settings

logger = setup_logger("WakeWord")

class WakeWordDetector:
    def __init__(self):
        # detector openwakeword multimodelo
        self.ww_general = settings["audio"].get("wake_word_general", "abril")
        self.ww_privado = settings["audio"].get("wake_word_privado", "escucha abril")
        logger.info(f"iniciando detector: general='{self.ww_general}', privado='{self.ww_privado}'")

    def listen(self):
        # escucha wake words simultaneamente
        logger.debug("escuchando...")
        # TODO: retornar 'Muted' si se activa ww_privado, de lo contrario 'Invitado'
        return "Invitado"
