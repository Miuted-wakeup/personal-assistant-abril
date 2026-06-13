import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pyaudio
import numpy as np
from openwakeword.model import Model
from backend.logger import setup_logger
from backend.config import settings

logger = setup_logger("WakeWord")

class WakeWordDetector:
    def __init__(self):
        self.ww_general = settings["audio"].get("wake_word_general", "abril")
        self.ww_privado = settings["audio"].get("wake_word_privado", "escucha abril")
        
        logger.info(f"Cargando modelos de Wake Word...")
        # Por defecto cargará los modelos integrados ('hey_jarvis', 'alexa', etc.)
        # Cuando entrenemos el modelo de Abril, lo pasaremos por argumento aquí.
        self.oww_model = Model(inference_framework="onnx")
        
        # Configuración de PyAudio para openWakeWord (16kHz, 16-bit, Mono)
        self.CHUNK = 1280
        self.audio = pyaudio.PyAudio()
        self.mic_stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        logger.info("Microfono activo y escuchando...")

    def listen(self):
        logger.debug("Esperando palabra de activacion...")
        while True:
            # Leer bloque de audio del micrófono
            audio_data = np.frombuffer(self.mic_stream.read(self.CHUNK, exception_on_overflow=False), dtype=np.int16)
            
            # Obtener predicciones
            prediction = self.oww_model.predict(audio_data)
            
            # Revisar si superó el umbral
            for mdl_name, score in prediction.items():
                if score > 0.5:  # 0.5 es un umbral estándar, se puede ajustar
                    logger.info(f"¡Wake Word detectada!: {mdl_name} (confianza: {score:.2f})")
                    # Para la prueba, asumiremos que si es jarvis/alexa o el que usemos, retorna al usuario Muted
                    return "Muted"

if __name__ == "__main__":
    print("Iniciando prueba aislada de Wake Word...")
    detector = WakeWordDetector()
    try:
        resultado = detector.listen()
        print(f"La escucha finalizó retornando: {resultado}")
    except KeyboardInterrupt:
        print("\nPrueba finalizada por el usuario.")
