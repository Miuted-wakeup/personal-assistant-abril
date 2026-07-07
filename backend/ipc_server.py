import socket
import json
from backend.logger import setup_logger

logger = setup_logger("IPC")

class StateNotifier:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def set_state(self, state):
        """Envía el nuevo estado de Abril (IDLE, ESCUCHANDO, PENSANDO, HABLANDO) al avatar."""
        try:
            message = json.dumps({"state": state.upper()}).encode('utf-8')
            self.sock.sendto(message, (self.host, self.port))
            logger.debug(f"Estado IPC enviado: {state}")
        except Exception as e:
            logger.error(f"Error enviando estado IPC: {e}")

# Instancia global para ser importada por otros módulos
notifier = StateNotifier()
