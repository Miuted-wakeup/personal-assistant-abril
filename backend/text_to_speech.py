import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import sounddevice as sd
from kokoro_onnx import Kokoro
from backend.logger import setup_logger

logger = setup_logger("TTS")

class TextToSpeech:
    def __init__(self):
        logger.info("Iniciando motor TTS Kokoro (v1.0)...")
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "kokoro-v1.0.onnx")
        self.voices_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "voices-v1.0.bin")
        
        if not os.path.exists(self.model_path):
            logger.error("El modelo Kokoro no se encuentra en la carpeta assets. Por favor descargalo primero.")
            self.kokoro = None
            return
            
        self.kokoro = Kokoro(self.model_path, self.voices_path)
        logger.info("Motor TTS listo.")

    def speak(self, text, voice="ef_dora"): # Voz femenina en español ('e' de Español, 'f' de Female)
        if not self.kokoro:
            logger.warning(f"Simulando voz (modelo no cargado): {text}")
            return
            
        logger.debug(f"Hablando: {text[:30]}...")
        # Generar audio
        # lang="es" es el código ISO para Español que espeak espera
        samples, sample_rate = self.kokoro.create(
            text, voice=voice, speed=1.0, lang="es" 
        )
        # Reproducir audio
        sd.play(samples, sample_rate)
        sd.wait()

if __name__ == "__main__":
    print("Iniciando prueba aislada de TTS...")
    tts = TextToSpeech()
    if tts.kokoro:
        tts.speak("Hola Gustavo. Todos los sistemas están operativos y mi módulo de voz está en línea.")
        print("Prueba finalizada.")
