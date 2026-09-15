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

## Arquitectura Hibrida

Le clavé Rust a la chingadera para que no tenga cuellos de botella mas que nada en la escucha y habla. Antes escuchaba usando Python y teníamos un uso de CPU de 5% al 10%, ahora usando Rust lo reducimos al 1% (o menos) siempre, locuron:

- **Orquestador Principal (Python):** Se encarga de la logica pesada, invocar a la IA, sintetizar la voz y gestionar la memoria vectorial. Es lento pero facil de iterar.
- **Microservicio de Hardware (Rust):** Un microservicio de muy bajo nivel que se comunica con el hardware (parlantes y microfono). Consume casi 0% de CPU y evita que Python se congele mientras procesa sonido o red.
- **Modulos de Inferencia:** Usamos openWakeWord para la deteccion local de palabras clave, Groq (Whisper) para la transcripcion en la nube super rapida y Kokoro-ONNX para el habla hiperrealista.
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
| **Rust Voice** | Exoesqueleto de muy bajo consumo para microfono y altavoces. | [Ver README](rust-voice-service/README.md) |
| **Assets** | Archivos estaticos y configuraciones de voz. | [Ver README](assets/README.md) |

## Estructura del Proyecto

```text
abril-asistente/
├── backend/
│   ├── main.py               # Orquestador principal (bucle de voz en vivo y CLI --texto)
│   ├── wake_word.py          # Detección de activación (modo hybrid_whisper / openWakeWord)
│   ├── speech_to_text.py     # Transcripción ultrarrápida con Whisper Turbo
│   ├── brain_llm.py          # Cerebro cognitivo (Groq / Hermes Agent con prompt adaptativo)
│   ├── hermes_client.py      # Cliente HTTP para el gateway de Hermes Agent
│   ├── web_search.py         # Búsqueda en internet en tiempo real (Brave Search)
│   ├── text_to_speech.py     # Síntesis local Kokoro-82M ONNX sanitizada para voz
│   ├── memory.py             # Gestor de memoria vectorial permanente (ChromaDB)
│   ├── ascii_frames.py       # Fotogramas de animación ASCII para consola
│   ├── ipc_server.py         # Servidor UDP para emisión de estados a la interfaz
│   ├── commands.py           # Control del sistema y comandos de utilidad
│   ├── automation.py         # Planificador de tareas proactivas (APScheduler)
│   ├── domotica.py           # Control de dispositivos locales por Wi-Fi (tinytuya)
│   ├── config.py             # Configuración centralizada de entorno
│   └── logger.py             # Sistema de logs con formato y niveles
├── rust-voice-service/       # Microservicio de hardware de ultra bajo consumo (Rust)
│   ├── src/
│   │   ├── main.rs           # Servidor TCP 9001 (Rodio audio) y TCP 9002 (VAD stream)
│   │   └── audio_input.rs    # Captura CPAL y VAD matemático puro (RMS + ZCR)
│   ├── Cargo.toml
│   └── README.md
├── discord-bot/
│   ├── bot.py                # Cliente de Discord
│   └── bridge.py             # Puente de comunicación con el orquestador
├── scripts/
│   ├── test_audio_completo.py    # Diagnóstico interactivo de niveles RMS, micrófono y Rust
│   ├── test_selective_memory.py  # Prueba de función calling y memoria selectiva en BD
│   ├── check_memory.py           # Inspector de recuerdos y metadatos en ChromaDB
│   ├── clean_chat_memories.py    # Limpiador de registros de chat obsoletos en ChromaDB
│   └── ver_memoria.py            # Inspector CLI tradicional de ChromaDB
├── assets/
│   ├── videos/               # idle.mp4, thinking.mp4, speaking.mp4 (para modo X11/mpv)
│   └── voices/               # custom_blend.json y modelos para Kokoro
├── data/
│   └── chromadb/             # Base de datos vectorial persistente local
├── avatar.py                 # Renderizador de rostro ASCII animado a 10 FPS
├── config.json               # Configuración del sistema (modos de audio, proveedores, etc.)
├── .env                      # Claves de API privadas (Groq, Brave Search, Discord)
├── requirements.txt          # Dependencias de Python
└── start_abril.sh            # Script de arranque en Linux (X11 + Openbox + mpv)
```

## Stack Tecnologico

| Componente | Tecnologia | Detalle |
|------------|------------|---------|
| Entrada y VAD | Rust (CPAL + RMS/ZCR) | Stream TCP 9002 continuo sin carga de CPU |
| Salida de Audio | Rust (Rodio) | Servidor TCP 9001 para reproducción asíncrona |
| Wake Word | Whisper Turbo / openWakeWord | Detección exacta de "Abril" / "Oye Abril" |
| STT | Groq Cloud API | whisper-large-v3-turbo (~300ms) |
| Cerebro / LLM | Groq Cloud API / Hermes Agent | openai/gpt-oss-20b con prompt adaptativo |
| TTS | Kokoro-82M ONNX | Voz local en español, sanitizada para habla fluida |
| Memoria | ChromaDB Local | Almacenamiento selectivo de hechos en 3ra persona |
| Busqueda Web | Brave Search API | Búsquedas en tiempo real vía function calling |
| Avatar | ASCII Engine / mpv IPC | Consola interactiva o video en pantalla dedicada |
| Backend | Python 3.11+ | Orquestador híbrido de lógica de negocio |

## Instalacion y Configuracion Base

1. **Clonar e inicializar entorno (Python)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Compilar Microservicio de Hardware (Rust)**:
   Requiere tener Rust instalado (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` o instalador de rustup en Windows):
   ```bash
   cd rust-voice-service
   cargo build --release
   cd ..
   ```

3. **Variables de Entorno (`.env`)**:
   Crea tu archivo `.env` en la raíz del proyecto:
   ```env
   GROQ_API_KEY=gsk_tu_clave_de_groq_aqui
   BRAVE_SEARCH_API_KEY=tu_clave_de_brave_search_aqui
   DISCORD_TOKEN=tu_token_de_discord_opcional
   ```

## Guia de Pruebas y Diagnostico

Al ser una arquitectura modular, puedes probar cada subsistema de forma independiente o correr el ciclo completo:

### 1. Ciclo de Voz en Vivo (Orquestador Completo)
Para hablar directamente con Abril usando tu micrófono y altavoces:
* **Terminal 1 (Microservicio de Hardware en Rust):**
  ```bash
  .\rust-voice-service\target\release\rust-voice-service.exe
  ```
* **Terminal 2 (Orquestador de Abril):**
  ```bash
  python backend/main.py
  ```
  Di *"Oye Abril"* o *"Abril"* seguido de tu comando (ej: *"Abril, ¿qué hora tienes?"* o *"Oye Abril, recuerda que mi color favorito es el negro"*).

### 2. Modo Texto de Prueba (Sin Audio ni Micrófono)
Para probar la lógica del cerebro, memoria y herramientas desde la consola interactiva por teclado:
```bash
python backend/main.py --texto
```

### 3. Diagnóstico de Audio y Micrófono
Verifica que el micrófono capture energía sonora, que el VAD matemático discrimine ruidos y que la salida por Rust reproduzca correctamente:
```bash
python scripts/test_audio_completo.py
```

### 4. Pruebas de Memoria Persistente (ChromaDB)
* **Validar guardado selectivo:** Comprueba que no se guarden conversaciones casuales y que solo se almacenen hechos personales:
  ```bash
  python scripts/test_selective_memory.py
  ```
* **Inspeccionar recuerdos guardados:**
  ```bash
  python scripts/check_memory.py
  ```
* **Limpiar recuerdos de chat obsoletos:**
  ```bash
  python scripts/clean_chat_memories.py
  ```

### 5. Pruebas de Componentes Aislados
* **Probar Wake Word:** `python backend/wake_word.py`
* **Probar Síntesis TTS:** `python backend/text_to_speech.py` (requiere Rust activo en el puerto 9001)
* **Probar Avatar ASCII:** `python avatar.py`
* **Probar Bot de Discord:** `python discord-bot/bot.py`

## Fases de Desarrollo y Planificacion

| Fase | Descripcion | Estado |
| :--- | :--- | :--- |
| **Fase 1-3** | Infraestructura, SO Linux Headless, SSH y Entorno | Completado |
| **Fase 4-6** | Wake Word local, Groq STT/LLM y TTS Kokoro ONNX | Completado |
| **Fase 7** | Memoria Persistente ChromaDB (Embeddings locales y memoria selectiva) | Completado |
| **Fase 8** | Avatar Visual interactivo (ASCII en consola a 10 FPS e IPC) | En progreso (70%) |
| **Fase 9** | Discord Bot (Cliente para integración remota) | Completado |
| **Fase 10**| Orquestación continua en vivo en main.py e instrumentación | Completado |
| **Fase 11A**| Salida de audio no bloqueante en Rust (Rodio TCP 9001) | Completado |
| **Fase 11B**| Captura y VAD matemático puro en Rust (CPAL TCP 9002) | Completado |
| **Fase 11C**| Integración de Hermes Agent (Cerebro persistente multi-canal) | En proceso |
| **Fase 12** | Dual Launcher (Consola Servidor 24/7 vs Desktop GUI) | Por hacer |
| **Fase 13** | Domótica Local por Wi-Fi (tinytuya) | Por hacer |
| **Fase 15** | Integración celular (KDE Connect) | Planeado |
| **Fase 16** | OpenClaw + MXC (Control remoto de la PC principal) | Por hacer |
| **Fase 17-18**| Sensores de Presencia y Sincronización de Cuentas | Planeado |

Para ver el desglose técnico y las tareas inmediatas de optimización, consulta el archivo [PLAN.md](PLAN.md).

## Agradecimientos y Creditos

La idea conceptual de crear un asistente con personalidad y memoria persistente está profundamente inspirada en el proyecto **[yui-asistente](https://github.com/EDAKZIN/yui-asistente)** creado por **[@EDAKZIN](https://github.com/EDAKZIN)**. **Abril** nace como una reimaginación enfocada exclusivamente en el **ultra bajo consumo**, ofreciendo una alternativa viable y altamente eficiente para equipos más humildes o con recursos limitados.

## Licencia: "Trátenmela Bien"

Copyright (c) 2026 Muted

Proyecto personal desarrollado por **Muted**, pero está ahí para quien quiera usarlo, clonarlo, estudiarlo o modificarlo a su gusto, nomás tratenmela bien :p

Las únicas condiciones son estas:

1. **Créditos:** Si tomas código de aquí, te basas en este proyecto o te lo vas a robar no me importa, pero al menos déjale los créditos a **Muted** y a los proyectos en los que se inspira (como `yui-asistente`) xfa ヾ(＾∇＾)
2. **Respeto:** Abril fue hecha con cariño para ser una compañera autónoma, directa y con personalidad en la habitación. Si la vas a modificar, respeta su esencia y no la conviertas en un bot aburrido, corporativo o censurado.

El código se entrega tal cual está. Si algo se rompe, tu PC explota o la IA cobra conciencia, es tu problema.


