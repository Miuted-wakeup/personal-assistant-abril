import sys
import os
import time
import json
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger
from backend.brain_llm import BrainLLM
from backend.speech_to_text import SpeechToText
from backend.text_to_speech import TextToSpeech
from backend.wake_word import WakeWordDetector
from backend.ipc_server import notifier

logger = setup_logger("Main")

class AbrilOrchestrator:
    def __init__(self, use_audio=True):
        self.state = "IDLE"
        self.use_audio = use_audio
        logger.info("Iniciando Abril Orchestrator")
        
        self.llm = None
        self.stt = None
        self.tts = None
        self.wake_word = None
        self.personality = {}
        
        self._init_modules()

    def _init_modules(self):
        logger.info("Cargando módulos de Abril...")
        self.llm = BrainLLM()
        
        if self.use_audio:
            self.stt = SpeechToText()
            self.tts = TextToSpeech()
            self.wake_word = WakeWordDetector()

        personality_path = os.path.join(os.path.dirname(__file__), "personality.json")
        try:
            with open(personality_path, "r", encoding="utf-8") as f:
                self.personality = json.load(f).get("transitions", {})
        except Exception as e:
            logger.warning(f"No se pudo cargar personality.json: {e}")
            self.personality = {"thinking": ["Un momento..."], "executing": ["Voy con ello."]}

    def transition_to(self, new_state):
        self.state = new_state
        
        ipc_map = {
            "IDLE": "IDLE",
            "LISTENING": "ESCUCHANDO",
            "TRANSCRIBING": "ESCUCHANDO",
            "THINKING": "PENSANDO",
            "HABLANDO": "HABLANDO",
            "SPEAKING": "HABLANDO"
        }
        ipc_state = ipc_map.get(new_state, "IDLE")
        notifier.set_state(ipc_state)
        return time.perf_counter()

    def get_filler_phrase(self, category):
        phrases = self.personality.get(category, ["..."])
        return random.choice(phrases)

    def run_voice_loop(self):
        # Bucle principal autonomo de voz
        logger.info("Bucle de voz en vivo activo. Di 'Oye Abril' o 'Abril' para hablar...")
        self.transition_to("IDLE")

        while True:
            try:
                self.transition_to("IDLE")
                logger.info(f"[{self.state}] Esperando palabra de activación ('Oye Abril' / 'Abril')...")
                
                activation = self.wake_word.listen()
                if not activation:
                    continue

                user_name, inline_command = activation
                t_start = time.perf_counter()

                if inline_command and inline_command.strip():
                    user_text = inline_command.strip()
                    logger.info(f"[Main] Comando capturado directamente en la activación: '{user_text}'")
                    t_transcribing = time.perf_counter()
                else:
                    t_listening = self.transition_to("LISTENING")
                    logger.info(f"[{self.state}] Activación sin comando posterior. Esperando petición de {user_name}...")
                    dur_cue = self.tts.speak("Dime.")
                    if dur_cue and dur_cue > 0:
                        time.sleep(dur_cue)

                    logger.info(f"[{self.state}] Escuchando comando de {user_name}...")
                    audio_wav = self.wake_word.record_speech(silence_timeout=1.1, max_duration=12.0)
                    if not audio_wav or not os.path.exists(audio_wav):
                        logger.warning("No se detectó audio posterior a la activación.")
                        continue

                    t_transcribing = self.transition_to("TRANSCRIBING")
                    user_text = self.stt.transcribe(audio_wav)
                    if not user_text or not user_text.strip():
                        logger.info("Transcripción vacía o inaudible.")
                        continue

                logger.info(f"[Usuario ({user_name})]: {user_text}")

                t_thinking = self.transition_to("THINKING")
                logger.info("[BrainLLM] Generando respuesta...")
                respuesta = self.llm.generate_response(user_text, user_name=user_name)
                if not respuesta or not respuesta.strip():
                    logger.warning("Respuesta vacía del LLM.")
                    continue

                logger.info(f"[Abril]: {respuesta}")

                t_speaking = self.transition_to("HABLANDO")
                t_synth_start = time.perf_counter()
                duracion_audio = self.tts.speak(respuesta)
                t_synth_end = time.perf_counter()

                if duracion_audio and duracion_audio > 0:
                    time.sleep(duracion_audio)

                t_end = time.perf_counter()
                ms_transcribe = (t_thinking - t_transcribing) * 1000
                ms_think = (t_speaking - t_thinking) * 1000
                ms_synth = (t_synth_end - t_synth_start) * 1000
                ms_playback = (duracion_audio * 1000) if duracion_audio else 0.0
                logger.info(f"[Instrumentación] Transcribe/Prep: {ms_transcribe:.1f}ms | Think(LLM): {ms_think:.1f}ms | Synth(TTS): {ms_synth:.1f}ms | Playback: {ms_playback:.1f}ms")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error en ciclo de voz: {e}")
                time.sleep(1)

        self._shutdown()

    def run_simulated_loop(self):
        # Bucle interactivo por texto CLI
        logger.info("Modo texto CLI interactivo. Escribe 'salir' para terminar.")
        current_user = "Muted"

        while True:
            try:
                self.transition_to("IDLE")
                user_input = input(f"\n[{self.state}] Escribe tu petición ({current_user}): ")
                if user_input.lower() in ["salir", "exit"]:
                    break

                t_start = self.transition_to("LISTENING")
                t_transcribing = self.transition_to("TRANSCRIBING")
                t_thinking = self.transition_to("THINKING")

                respuesta = self.llm.generate_response(user_input, user_name=current_user)
                t_speaking = self.transition_to("HABLANDO")
                print(f"\nAbril: {respuesta}\n")

                if self.tts:
                    duracion = self.tts.speak(respuesta)
                    time.sleep(duracion)
                else:
                    time.sleep(1.0)

                t_end = time.perf_counter()
                ms_think = (t_speaking - t_thinking) * 1000
                logger.info(f"[Instrumentación] Think(LLM): {ms_think:.1f}ms")

            except KeyboardInterrupt:
                break

        self._shutdown()

    def _shutdown(self):
        logger.info("Apagando orquestador de Abril...")
        self.transition_to("IDLE")
        if self.wake_word:
            self.wake_word.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Orquestador del Asistente Virtual Abril")
    parser.add_argument("--texto", action="store_true", help="Ejecutar en modo consola de texto sin micrófono")
    args = parser.parse_args()

    if args.texto:
        orchestrator = AbrilOrchestrator(use_audio=False)
        orchestrator.run_simulated_loop()
    else:
        orchestrator = AbrilOrchestrator(use_audio=True)
        orchestrator.run_voice_loop()
