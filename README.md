# Asistente Virtual Autonomo: Abril

> **Filosofia de Ultra Bajo Consumo**: A diferencia de otros asistentes que requieren hardware de ultima generacion y decenas de gigabytes de VRAM (como Yui), Abril esta disenada desde cero para la eficiencia absoluta. Delegando la carga pesada a la nube y manteniendo interfaces locales ultraligeras, corre perfectamente 24/7 en procesadores de hace mas de una decada.

Este es el repositorio del proyecto **Abril**, un asistente de voz inteligente, autonomo y de presencia fisica constante 24/7 en habitacion, disenado bajo una arquitectura hibrida local/nube para optimizar recursos en hardware limitado. Creado por **Muted**.

## Caracteristicas

- **Wake Word Local**: openWakeWord para deteccion de palabras clave sin consumo de internet ("Abril", "Escucha Abril").
- **STT (Speech-to-Text)**: Groq API con Whisper-large-v3 para transcripcion ultra rapida.
- **LLM**: Llama 3.1 8B Instant via Groq API.
- **TTS**: Kokoro-82M ONNX local para sintesis de voz natural en espanol sin latencia de red.
- **Busqueda Web**: Integracion con Brave Search API mediante Function Calling.
- **Personalidad Unica**: Prompt dinamico adaptado a Muted y a invitados en la habitacion.
- **Modo Texto de Prueba**: CLI integrado para pruebas de logica sin hardware de audio.
- **Avatar Visual**: Reproduccion de video dinamica mediante mpv e IPC sincronizado con el estado del asistente.

## Pipeline Principal

```text
Usuario -> openWakeWord -> Groq STT -> Groq LLM (Llama 3.1) -> Kokoro TTS -> Audio
  habla      (local)        (nube)         (nube)               (local)     (respuesta)
```

## Especificaciones de Hardware Base

El proyecto se esta desarrollando y probando sobre el siguiente hardware de referencia. Si tienes especificaciones por encima de estas, vas sobrado:

- **CPU**: Intel Core i7 de 2ª Generacion
- **GPU**: NVIDIA GeForce GTX 960
- **RAM**: 12 GB DDR3 a 2666 MT/s
- **Almacenamiento**: SSD de 125 GB
- **Pantalla**: Mini pantalla dedicada de 7-10 pulgadas conectada por HDMI
- **Perifericos**: Microfono ambiental USB y parlantes por Jack de 3.5mm o USB

## Modulos y Documentacion Secundaria

La arquitectura esta dividida en modulos independientes. Consulta los siguientes README para mas detalle tecnico:

| Modulo / Carpeta | Descripcion | Enlace |
|------------------|-------------|--------|
| **Plan Maestro** | Fases detalladas, tiempos y especificaciones originales. | [Ver Plan](PLAN.md) |
| **Backend** | Orquestador, LLM, STT, TTS y herramientas. | [Ver README](backend/README.md) |
| **Discord Bot** | Cliente para integracion remota. | [Ver README](discord-bot/README.md) |
| **Assets** | Videos del avatar y configuraciones de voz. | [Ver README](assets/README.md) |

## Estructura del Proyecto

```text
abril-asistente/
├── backend/
│   ├── main.py               # Orquestador principal y CLI de pruebas
│   ├── wake_word.py          # Escucha activa (openWakeWord multimodelo)
│   ├── speech_to_text.py     # Cliente Groq Whisper API
│   ├── brain_llm.py          # Cliente Groq LLM (Llama 3.1 con prompt dinamico)
│   ├── web_search.py         # Busqueda en internet (Brave Search)
│   ├── text_to_speech.py     # Motor local Kokoro-82M
│   ├── memory_system.py      # Base de datos vectorial (ChromaDB)
│   ├── visual_controller.py  # Controlador de mpv via IPC
│   ├── commands.py           # Control del sistema y llamadas de utilidad
│   ├── automation.py         # Planificador de tareas proactivas (APScheduler)
│   ├── domotica.py           # Control de dispositivos locales (tinytuya)
│   ├── config.py             # Configuracion centralizada
│   └── logger.py             # Logs del sistema con colorlog
├── discord-bot/
│   ├── bot.py                # Cliente de Discord
│   └── bridge.py             # Enlace de mensajes con el backend
├── assets/
│   ├── videos/               # idle.mp4, thinking.mp4, speaking.mp4
│   └── voices/               # custom_blend.json para Kokoro
├── data/
│   └── chromadb/             # Base de datos local
├── config.json               # Configuracion (APIs, audio, entorno)
├── .env                      # API Keys (Groq, Brave Search, Discord Token)
├── requirements.txt          # Dependencias de Python
└── start_abril.sh            # Script de arranque del sistema (X11 + mpv)
```

## Stack Tecnologico

| Componente | Tecnologia |
|------------|------------|
| STT | Groq API (Whisper-large-v3) |
| LLM | Groq API (Llama-3.1-8b-instant) |
| TTS | Kokoro-82M ONNX (Espanol local) |
| Wake Word | openWakeWord (Modelos ONNX locales) |
| Busqueda Web | Brave Search API |
| Backend | Python 3.11+ |
| Interfaz Grafica | mpv (IPC control) sobre X11/Openbox |
| Domotica | tinytuya (Control LAN local) |

## Instalacion y Configuracion Base

1. **Clonar e inicializar entorno**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Variables de Entorno**:
   Crear un archivo `.env` en la raiz con las siguientes claves:
   ```text
   GROQ_API_KEY=tu_api_key
   BRAVE_SEARCH_API_KEY=tu_api_key
   DISCORD_TOKEN=tu_token
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

3. **Ejecucion en Modo Prueba (Sin Audio)**:
   ```bash
   python backend/main.py
   ```

## Fases de Desarrollo y Planificacion

| Fase | Descripcion | Estado |
| :--- | :--- | :--- |
| **Fase 1-3** | Infraestructura, SO Linux Headless, SSH y Entorno | Planeado |
| **Fase 4** | Entrada de Audio y Wake Word Local (Multi-modelo) | En Progreso |
| **Fase 5** | Conexion Nube Groq STT/LLM y Prompt Dinamico | Completado |
| **Fase 6** | Motor TTS Local (Kokoro ONNX) | Planeado |
| **Fase 7-8** | Memoria ChromaDB e Interfaz Visual IPC | Planeado |
| **Fase 9-10** | Discord Bot y Orquestacion Principal (systemd) | En Progreso |
| **Fase 11+** | Domotica LAN, Eventos Proactivos y Vision | Planeado |

## Licencia

Proyecto personal desarrollado por **Muted**.
