import os
from groq import Groq
from backend.logger import setup_logger
from backend.config import GROQ_API_KEY, settings

logger = setup_logger("STT")

class SpeechToText:
    def __init__(self):
        # stt via groq whisper
        logger.info(f"iniciando stt: {settings['apis']['groq_model_stt']}")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = settings['apis']['groq_model_stt']

    def transcribe(self, audio_filepath):
        # transcribe audio a texto
        logger.debug(f"transcribiendo: {audio_filepath}")
        
        if not os.path.exists(audio_filepath):
            logger.error(f"no existe archivo: {audio_filepath}")
            return ""
            
        try:
            with open(audio_filepath, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                  file=(os.path.basename(audio_filepath), file.read()),
                  model=self.model,
                  language="es"
                )
            texto = transcription.text
            logger.debug(f"texto stt: {texto}")
            return texto
        except Exception as e:
            logger.error(f"error en stt: {e}")
            return ""
