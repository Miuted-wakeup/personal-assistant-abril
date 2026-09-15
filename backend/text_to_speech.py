import sys
import os
import re
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
        if not text or not text.strip():
            return 0.0

        clean_text = re.sub(r'[*_#`~]', '', text).strip()
        if not clean_text:
            return 0.0

        if not self.kokoro:
            logger.warning(f"Simulando voz (modelo no cargado): {clean_text}")
            return 0.0
            
        logger.debug(f"Hablando: {clean_text[:30]}...")
        # Generar audio
        # lang="es" es el código ISO para Español que espeak espera
        samples, sample_rate = self.kokoro.create(
            clean_text, voice=voice, speed=1.05, lang="es" 
        )
        duration = len(samples) / float(sample_rate)

        # Intentar enviar el audio al Exoesqueleto de Rust
        import socket
        import io
        import soundfile as sf
        
        try:
            # Convertir el array numpy a un archivo WAV en memoria
            wav_io = io.BytesIO()
            sf.write(wav_io, samples, sample_rate, format='wav')
            
            # Enviar los bytes por TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect(('127.0.0.1', 9001))
                s.sendall(wav_io.getvalue())
                logger.debug("Audio enviado a Rust exitosamente (No bloqueante).")
                
        except (ConnectionRefusedError, socket.timeout):
            logger.warning("Rust Exo-skeleton no detectado en el puerto 9001. Usando sounddevice (bloqueante)...")
            sd.play(samples, sample_rate)
            sd.wait()

        return duration
if __name__ == "__main__":
    print("Iniciando prueba aislada de TTS...")
    tts = TextToSpeech()
    if tts.kokoro:
        tts.speak("Hola Gustavo. Todos los sistemas están operativos y mi módulo de voz está en línea.")
        print("Prueba finalizada.")
