import sys
import os
import time
import socket
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger

logger = setup_logger("TestAudio")

def test_salida_audio(host="127.0.0.1", port=9001):
    print("\n--- PRUEBA 1: Salida de Audio (TCP 9001) ---")
    try:
        from backend.text_to_speech import TextToSpeech
        print("Cargando motor TTS...")
        tts = TextToSpeech()
        frase = "Hola Muted. El microservicio de Rust esta activo y la salida de audio funciona correctamente."
        print(f"Enviando frase de prueba: '{frase}'")
        tts.speak(frase)
        print("Audio enviado al servidor de Rust. Si escuchaste a Abril, la salida funciona.")
    except Exception as e:
        print(f"Error en prueba de salida: {e}")

def test_stream_microfono(host="127.0.0.1", port=9002, duracion_segundos=10):
    print(f"\n--- PRUEBA 2: Entrada de Micrófono & VAD (TCP {port}) ---")
    print(f"Conectando a {host}:{port}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((host, port))
        print("Conectado con exito al stream de Rust.")
        print("Habla por tu microfono. Rust enviara datos unicamente cuando detecte voz.")
        print(f"Monitoreando durante {duracion_segundos} segundos...\n")
        
        chunk_bytes = 1280 * 2 # 80ms a 16kHz
        start_time = time.time()
        paquetes_recibidos = 0
        
        sock.settimeout(1.0)
        
        while time.time() - start_time < duracion_segundos:
            try:
                data = bytearray()
                while len(data) < chunk_bytes:
                    packet = sock.recv(chunk_bytes - len(data))
                    if not packet:
                        break
                    data.extend(packet)
                    
                if len(data) == chunk_bytes:
                    paquetes_recibidos += 1
                    samples = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean((samples.astype(np.float32) / 32768.0) ** 2))
                    bar_len = int(min(rms * 100, 30))
                    barra = "#" * bar_len + "-" * (30 - bar_len)
                    print(f"\r[Voz Activa] Cuadro #{paquetes_recibidos:03d} | RMS: {rms:.4f} | [{barra}]", end="", flush=True)
            except socket.timeout:
                print("\r[Silencio / Esperando voz...]                                          ", end="", flush=True)
                
        print(f"\n\nPrueba finalizada. Total de cuadros de voz recibidos: {paquetes_recibidos}")
        sock.close()
        
    except ConnectionRefusedError:
        print(f"No se pudo conectar a {host}:{port}. Asegurate de que rust-voice-service este corriendo.")
    except Exception as e:
        print(f"Error durante la prueba de entrada: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("      DIAGNÓSTICO DEL SISTEMA DE AUDIO RUST       ")
    print("==================================================")
    print("1. Probar Salida de Audio (TTS -> Rust 9001)")
    print("2. Probar Entrada de Micrófono & VAD (Rust 9002)")
    print("3. Ejecutar ambas pruebas")
    
    opcion = input("\nSelecciona una opción (1, 2 o 3): ").strip()
    
    if opcion == "1":
        test_salida_audio()
    elif opcion == "2":
        test_stream_microfono()
    elif opcion == "3":
        test_salida_audio()
        time.sleep(2)
        test_stream_microfono()
    else:
        print("Opción no válida.")
