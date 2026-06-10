from backend.logger import setup_logger

logger = setup_logger("TTS")

class TextToSpeech:
    def __init__(self):
        # motor tts local kokoro
        logger.info("iniciando tts kokoro")

    def speak(self, text):
        # texto a voz
        logger.debug(f"hablando: {text[:20]}")
        pass
