# Asistente Virtual Autonomo: Abril

> **Filosofia de Ultra Bajo Consumo**: A diferencia de otros asistentes de IA actuales que exigen hardware de ultima generacion y decenas de gigabytes de VRAM, Abril esta disenada desde cero para la eficiencia absoluta. Delegando el razonamiento a la nube a traves de APIs ultrarrapidas y manteniendo interfaces locales hiper-optimizadas, corre perfectamente 24/7 en procesadores de hace mas de una decada.

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

*Nota: Aunque actualmente el proyecto se esta estructurando sobre este PC humilde, la idea principal a futuro es implementarlo en una Raspberry Pi bastante capaz para tener una version miniatura de consumo ultra bajo que siga funcionando sin internet usando el WiFi como via de transmision para los componentes inteligentes de la habitacion.*

## Modulos y Documentacion Secundaria

La arquitectura esta dividida en modulos independientes. Consulta los siguientes README para mas detalle tecnico:

| Modulo / Carpeta | Descripcion | Enlace |
|------------------|-------------|--------|
| **Plan Malevolo** | Fases detalladas, tiempos y especificaciones originales. | [Ver Plan](PLAN.md) |
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
│   ├── memory.py             # Base de datos vectorial (ChromaDB)
│   ├── ascii_frames.py       # Librería de fotogramas ASCII
│   ├── ipc_server.py         # Servidor de notificaciones de estado por UDP
│   ├── commands.py           # Control del sistema y llamadas de utilidad
│   ├── automation.py         # Planificador de tareas proactivas (APScheduler)
│   ├── domotica.py           # Control de dispositivos locales (tinytuya)
│   ├── config.py             # Configuracion centralizada
│   └── logger.py             # Logs del sistema con colorlog
├── discord-bot/
│   ├── bot.py                # Cliente de Discord
│   └── bridge.py             # Enlace de mensajes con el backend
├── scripts/
│   └── ver_memoria.py        # Inspector de base de datos de memoria
├── assets/
│   ├── videos/               # idle.mp4, thinking.mp4, speaking.mp4
│   └── voices/               # custom_blend.json para Kokoro
├── data/
│   └── chromadb/             # Base de datos local
├── avatar.py                 # Renderizador del avatar animado ASCII en consola
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

2. **Descarga de Modelos y Configuración Automática**:
   Ejecuta el script de inicialización para descargar la red neuronal de Kokoro (TTS) y generar tu plantilla de variables de entorno:
   ```bash
   python setup.py
   ```
   
   **¿Dónde obtener las claves para el `.env`?**
   Abre el archivo `.env` recién creado y llénalo:
   - **GROQ_API_KEY**: Crea una cuenta gratuita en [GroqCloud Console](https://console.groq.com/keys) para tener acceso a los modelos Llama ultrarrápidos.
   - **BRAVE_SEARCH_API_KEY**: Regístrate en el [Brave Search API Portal](https://api.search.brave.com/app/keys) y obtén una llave para la capa gratuita (Free Data API, hasta 2000 consultas/mes).
   - **DISCORD_TOKEN**: Entra al [Discord Developer Portal](https://discord.com/developers/applications), crea una App, ve a la pestaña "Bot" y haz clic en "Reset Token". *(Importante: Debes encender los tres "Privileged Gateway Intents" en esa misma página).*

3. **Ejecucion en Modo Prueba (Sin Audio)**:
   ```bash
   python backend/main.py
   ```

4. **Pruebas de Módulos Individuales**:
   Como la arquitectura es modular, puedes probar cada sentido de Abril por separado:
   - **Probar Wake Word (Oído)**: Ejecuta `python backend/wake_word.py`. Habla por tu micrófono (temporalmente detecta "Alexa" o "Hey Mycroft" mientras entrenamos la palabra "Abril").
   - **Probar Síntesis de Voz (Habla)**: Ejecuta `python backend/text_to_speech.py`. Sintetizará y reproducirá una frase de prueba en español de forma totalmente local.
   - **Probar Puente de Discord (Telepatía)**: Ejecuta `python discord-bot/bot.py`. Abril se pondrá en línea en tu servidor y te responderá si la mencionas (`@Abril`) o si le escribes por Mensaje Directo.
   - **Probar Memoria (Hipocampo)**: Ejecuta `python scripts/ver_memoria.py`. Inspecciona y muestra todos los recuerdos que Abril ha guardado sobre ti en ChromaDB en texto claro.
   - **Probar Avatar ASCII (Cara)**: Ejecuta `python avatar.py`. Abre la cara virtual de Abril en consola, la cual reaccionará en tiempo real al estado del bot de Discord a 10 FPS.

## Fases de Desarrollo y Planificacion

| Fase | Descripcion | Estado |
| :--- | :--- | :--- |
| **Fase 1-3** | Infraestructura, SO Linux Headless, SSH y Entorno | Completado |
| **Fase 4** | Entrada de Audio y Wake Word Local (Multi-modelo) | Completado |
| **Fase 5** | Conexion Nube Groq STT/LLM y Prompt Dinamico | Completado |
| **Fase 6** | Motor TTS Local (Kokoro ONNX) | Completado |
| **Fase 7** | Memoria Persistente ChromaDB (Embeddings locales) | Completado |
| **Fase 8** | Avatar Visual interactivo en consola (Anime ASCII) | En Desarrollo (~70%) |
| **Fase 9** | Discord Bot (Cliente para integracion remota) | Completado |
| **Fase 10**| Orquestacion Principal (systemd) | Planeado |
| **Fase 11-15**| Domotica LAN, Eventos Proactivos y Vision | Planeado |
| **Fase 16-18**| OpenClaw, Sensores de Presencia y Cuentas | Planeado |

## Agradecimientos y Creditos

La idea conceptual de crear un asistente con personalidad y memoria persistente esta profundamente inspirada en el proyecto **[yui-asistente](https://github.com/EDAKZIN/yui-asistente)** creado por **[@EDAKZIN](https://github.com/EDAKZIN)**. **Abril** nace como una reimaginacion enfocada exclusivamente en el **ultra bajo consumo**, ofreciendo una alternativa viable y altamente eficiente para equipos mas humildes o con recursos limitados.

## Licencia

Proyecto personal desarrollado por **Muted**.
