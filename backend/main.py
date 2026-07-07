import sys
import os
import time

# agrega directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger
from backend.brain_llm import BrainLLM
from backend.ipc_server import notifier

logger = setup_logger("Main")

class AbrilAssistant:
    def __init__(self):
        # maquina de estados principal
        self.state = "ESPERA"
        logger.info("iniciando abril")
        self.llm = None
        self._init_modules()

    def _init_modules(self):
        # carga dependencias
        logger.info("cargando modulos")
        self.llm = BrainLLM()

    def test_text_mode(self):
        # prueba en consola sin hardware de audio
        logger.info("modo texto activo (escribe 'salir' para terminar)")
        current_user = "Muted"
        logger.info(f"usuario actual: {current_user} (escribe '/user Nombre' para cambiar de persona)")
        
        while True:
            try:
                user_input = input(f"\n{current_user}: ")
                if user_input.lower() in ["salir", "exit"]:
                    break
                
                if user_input.startswith("/user "):
                    current_user = user_input.split(" ", 1)[1]
                    logger.info(f"cambio de usuario a: {current_user}")
                    continue
                
                notifier.set_state("PENSANDO")
                respuesta = self.llm.generate_response(user_input, user_name=current_user)
                
                notifier.set_state("HABLANDO")
                print(f"\nAbril: {respuesta}")
                
                # Simulamos el tiempo de habla (en el futuro esto lo definirá la longitud del audio)
                time.sleep(2)
                notifier.set_state("IDLE")
                
            except KeyboardInterrupt:
                break
        
        logger.info("apagando abril")

    def run(self):
        # NOTE: Este esqueleto está reservado para la Fase 10 (Orquestación del ciclo continuo en hardware).
        # Actualmente, iniciamos en modo texto directo por consola.
        logger.info("abril en linea (ejecución continua de hardware no integrada aún)")
        try:
            while True:
                # Mantener el proceso vivo.
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("apagando abril")

if __name__ == "__main__":
    assistant = AbrilAssistant()
    # usamos modo texto temporalmente para probar el llm en tu maquina
    assistant.test_text_mode()
