import sys
import os
import time
import socket
import re
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger
from backend.config import settings

logger = setup_logger("WakeWord")

class WakeWordDetector:
    def __init__(self, rust_host="127.0.0.1", rust_port=9002):
        audio_cfg = settings.get("audio", {})
        self.mode = audio_cfg.get("wake_word_mode", "hybrid_whisper")
        self.oww_model_name = audio_cfg.get("openwakeword_model", "alexa")
        self.oww_threshold = float(audio_cfg.get("openwakeword_threshold", 0.85))
        
        self.CHUNK = 1280
        self.CHUNK_BYTES = self.CHUNK * 2
        
        self.use_rust_stream = False
        self.rust_socket = None
        self.audio = None
        self.mic_stream = None
        self.oww_model = None
        self.stt = None

        if self.mode == "hybrid_whisper":
            logger.info("Modo Wake Word: 'hybrid_whisper' (detección exacta de 'Abril' / 'Oye Abril' con Whisper).")
            from backend.speech_to_text import SpeechToText
            self.stt = SpeechToText()
        else:
            logger.info(f"Modo Wake Word: 'openwakeword' (modelo: {self.oww_model_name}, umbral: {self.oww_threshold}).")
            from openwakeword.model import Model
            self.oww_model = Model(wakeword_models=[self.oww_model_name], inference_framework="onnx")

        self._init_audio_source(rust_host, rust_port)

    def _init_audio_source(self, host, port):
        # Intento de conexión al socket de streaming de Rust
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.5)
            sock.connect((host, port))
            sock.settimeout(None)
            self.rust_socket = sock
            self.use_rust_stream = True
            logger.info(f"Conectado al stream de Rust en {host}:{port} con VAD matemático.")
            return
        except (ConnectionRefusedError, socket.timeout, OSError):
            logger.warning(f"Microservicio de Rust no disponible en {host}:{port}. Activando fallback a PyAudio.")

        self._init_pyaudio_fallback()

    def _init_pyaudio_fallback(self):
        try:
            import pyaudio
            self.audio = pyaudio.PyAudio()
            self.mic_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            logger.info("Micrófono local activo mediante PyAudio.")
        except Exception as e:
            logger.error(f"Error inicializando PyAudio: {e}")

    def _read_from_rust(self):
        buf = bytearray()
        while len(buf) < self.CHUNK_BYTES:
            packet = self.rust_socket.recv(self.CHUNK_BYTES - len(buf))
            if not packet:
                raise ConnectionResetError("Stream de audio en Rust cerrado.")
            buf.extend(packet)
        return bytes(buf)

    def record_speech(self, silence_timeout=1.1, max_duration=12.0):
        # Graba flujo de voz hasta detectar una pausa de silencio
        frames = []
        start_time = time.time()

        if self.use_rust_stream and self.rust_socket:
            try:
                self.rust_socket.settimeout(silence_timeout)
                while time.time() - start_time < max_duration:
                    try:
                        chunk = self._read_from_rust()
                        frames.append(chunk)
                    except (socket.timeout, TimeoutError):
                        break
            except Exception as e:
                logger.warning(f"Error grabando de stream de Rust: {e}")
            finally:
                if self.rust_socket:
                    try:
                        self.rust_socket.settimeout(None)
                    except Exception:
                        pass
        elif self.mic_stream:
            silence_counter = 0.0
            chunk_sec = self.CHUNK / 16000.0
            while time.time() - start_time < max_duration:
                chunk = self.mic_stream.read(self.CHUNK, exception_on_overflow=False)
                samples = np.frombuffer(chunk, dtype=np.int16)
                rms = np.sqrt(np.mean((samples.astype(np.float32) / 32768.0) ** 2))
                if rms > 0.015:
                    frames.append(chunk)
                    silence_counter = 0.0
                else:
                    if len(frames) > 0:
                        frames.append(chunk)
                        silence_counter += chunk_sec
                        if silence_counter >= silence_timeout:
                            break
                    else:
                        silence_counter += chunk_sec
                        if silence_counter >= silence_timeout:
                            break

        if not frames:
            return None

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        wav_path = os.path.join(data_dir, "temp_command.wav")

        import wave
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b"".join(frames))

        return wav_path

    def listen(self):
        # Escucha y valida palabra de activación
        if self.mode == "hybrid_whisper":
            return self._listen_hybrid_whisper()
        else:
            return self._listen_openwakeword()

    def _listen_hybrid_whisper(self):
        while True:
            try:
                # Rust sólo envía cuadros cuando hay voz activa
                wav_path = self.record_speech(silence_timeout=1.1, max_duration=6.0)
                if not wav_path or not os.path.exists(wav_path):
                    continue

                transcription = self.stt.transcribe(wav_path)
                if not transcription or not transcription.strip():
                    continue

                clean_text = transcription.strip()
                
                # Comprobar si menciona "abril"
                if re.search(r'\babril\b', clean_text, re.IGNORECASE):
                    # Extraer comando si se dijo en la misma frase
                    raw_cmd = re.sub(r'^(oye|hola|escucha)?[\s,]*abril[\s,]*', '', clean_text, flags=re.IGNORECASE).strip()
                    # Limpiar puntuación inicial o final
                    inline_command = re.sub(r'^[^\w]+|[^\w]+$', '', raw_cmd).strip()
                    if not re.search(r'\w', inline_command):
                        inline_command = ""
                    logger.info(f"[WakeWord] Activación confirmada: '{clean_text}'" + (f" -> Comando: '{inline_command}'" if inline_command else " (Llamada inicial)"))
                    return ("Muted", inline_command)
                else:
                    logger.info(f"[WakeWord] Descartado: '{clean_text}' (No contiene palabra clave 'Abril').")

            except (ConnectionResetError, BrokenPipeError, socket.error) as e:
                logger.warning(f"Fallo en stream de Rust ({e}). Fallback a PyAudio...")
                self.use_rust_stream = False
                if self.rust_socket:
                    try:
                        self.rust_socket.close()
                    except Exception:
                        pass
                    self.rust_socket = None
                self._init_pyaudio_fallback()

    def _listen_openwakeword(self):
        while True:
            try:
                if self.use_rust_stream and self.rust_socket:
                    raw_bytes = self._read_from_rust()
                elif self.mic_stream:
                    raw_bytes = self.mic_stream.read(self.CHUNK, exception_on_overflow=False)
                else:
                    logger.error("No hay fuente de audio disponible.")
                    return None

                audio_data = np.frombuffer(raw_bytes, dtype=np.int16)
                prediction = self.oww_model.predict(audio_data)

                for mdl_name, score in prediction.items():
                    if score >= self.oww_threshold:
                        logger.info(f"[WakeWord] Detectada {mdl_name} con confianza {score:.2f} (Umbral: {self.oww_threshold})")
                        return ("Muted", "")

            except (ConnectionResetError, BrokenPipeError, socket.error) as e:
                logger.warning(f"Fallo en stream de Rust ({e}). Fallback a PyAudio...")
                self.use_rust_stream = False
                if self.rust_socket:
                    try:
                        self.rust_socket.close()
                    except Exception:
                        pass
                    self.rust_socket = None
                self._init_pyaudio_fallback()

    def close(self):
        if self.rust_socket:
            try:
                self.rust_socket.close()
            except Exception:
                pass
        if self.mic_stream:
            try:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
            except Exception:
                pass
        if self.audio:
            try:
                self.audio.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    print("Iniciando prueba de Wake Word con filtro estricto...")
    detector = WakeWordDetector()
    try:
        user, cmd = detector.listen()
        print(f"Detectado usuario: {user} | Comando en linea: '{cmd}'")
    except KeyboardInterrupt:
        print("\nPrueba finalizada.")
    finally:
        detector.close()
