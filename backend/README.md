# Backend: Orquestacion y Logica Principal

Este directorio contiene los modulos centrales que dan vida a Abril.

## Modulos Principales

| Archivo | Proposito |
|---------|-----------|
| `main.py` | Maquina de estados central y ciclo de ejecucion (CLI de pruebas). |
| `wake_word.py` | Interfaz con openWakeWord para detectar multiples activadores. |
| `speech_to_text.py` | Envio de comandos de voz grabados a Groq Whisper. |
| `brain_llm.py` | Logica de Llama 3.1 con prompt dinamico, memoria a corto plazo y busqueda web. |
| `web_search.py` | Herramienta de busqueda en internet conectada a Brave Search API. |
| `text_to_speech.py` | Generacion de audio local con Kokoro-82M ONNX. |
| `config.py` / `logger.py` | Utilidades de configuracion y formateo de logs con colorlog. |

## Interaccion entre modulos
El orquestador (`main.py`) controla el flujo pasando los datos de voz al STT, luego el texto al LLM, y finalmente la respuesta al TTS, mientras notifica a los controladores visuales.
