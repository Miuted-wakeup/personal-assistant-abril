import socket
import json
import time
import os
import threading
import sys

# Importar los fotogramas (frames) desde nuestra librería
from backend.ascii_frames import FRAMES

current_state = "IDLE"

def listen_ipc(host='127.0.0.1', port=65432):
    global current_state
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
        #print(f"[IPC] Escuchando estados en {host}:{port}")
    except OSError as e:
        print(f"[Error IPC] No se pudo vincular al puerto {port}: {e}")
        return

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            message = json.loads(data.decode('utf-8'))
            if "state" in message and message["state"] in FRAMES:
                current_state = message["state"]
        except Exception as e:
            pass

def draw_avatar():
    # Ocultar cursor y limpiar pantalla para evitar parpadeos
    sys.stdout.write('\033[?25l')
    os.system('cls' if os.name == 'nt' else 'clear')
    
    frame_idx = 0
    fps = 10 # 10 fotogramas por segundo
    
    try:
        while True:
            # Mover el cursor al inicio (código de escape ANSI) para sobreescribir sin borrar
            sys.stdout.write('\033[H')
            
            print("\n" + "="*40)
            print("         ABRIL AVATAR VIRTUAL         ")
            print("="*40)
            print(f"\nEstado Actual: [{current_state}]\n")
            
            animacion = FRAMES.get(current_state, FRAMES["IDLE"])
            
            # Lógica de animación: IDLE parpadea poco, HABLANDO mueve la boca rápido
            if current_state == "IDLE":
                if frame_idx % 40 < 38: # Ojos abiertos el 95% del tiempo
                    frame_ascii = animacion[0]
                else:                   # Parpadeo rápido
                    frame_ascii = animacion[1]
            else:
                frame_ascii = animacion[(frame_idx // 2) % len(animacion)]
                
            print(frame_ascii)
            
            print("\n" + "="*40)
            print("Presiona Ctrl+C para salir.")
            
            sys.stdout.flush()
            frame_idx += 1
            time.sleep(1.0 / fps)
    finally:
        sys.stdout.write('\033[?25h') # Restaurar cursor al salir

if __name__ == "__main__":
    t = threading.Thread(target=listen_ipc, daemon=True)
    t.start()
    
    try:
        draw_avatar()
    except KeyboardInterrupt:
        print("\nApagando Avatar...")
        sys.exit(0)
