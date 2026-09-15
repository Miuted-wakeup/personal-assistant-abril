# Plan de Implementacion y Fases de Desarrollo

Este documento contiene la planificación original y detallada de todas las fases del proyecto Abril, desde la infraestructura física hasta los módulos más avanzados.

## Estado General del Proyecto
- **Fase 1 a 3 (Entorno y OS):** Completado.
- **Fase 4 a 6 (Audio, LLM, TTS):** Completado.
- **Fase 7 (Memoria ChromaDB):** Completado (100% - Persistente con tiempo relativo y filtro anti-loro).
- **Fase 8 (Avatar Visual IPC):** Completado temporalmente en consola (70% - Chica Anime ASCII a 10 FPS fluida sobre IPC).
- **Fase 9 (Bot Discord):** Completado (100% - Conexión por MD y Servidores).
- **Fase 10 (Orquestación continua):** Completado (100% - Bucle de voz en vivo en main.py con instrumentación y máquina de estados IPC).
- **Fase 11 (Microservicio Rust Exoesqueleto):** Completado (100% - Fase 11A Salida Rodio 9001 + Fase 11B Entrada CPAL con VAD matemático RMS/ZCR 9002).
- **Fase 11C (Integración Hermes Agent):** En proceso (Cerebro persistente multi-canal y scheduler proactivo agnóstico de modelos).
- **Fase 12 (Dual Launcher - Servidor vs Desktop):** Por hacer (Modo Servidor Consola Headless 24/7 y Launcher Desktop con selector de proveedores y modelos locales).
- **Fase 13 (Domótica Local):** Por hacer (Control de luces y enchufes inteligentes por Wi-Fi mediante tinytuya).
- **Fase 16 (Integración OpenClaw + PC Principal):** Por hacer (Control remoto de la computadora diaria en sandbox MXC).

## Filosofia y Arquitectura Base
Antes de avanzar a los modulos complejos, el proyecto se rige por los siguientes principios para garantizar que la V1 sea rapida, estable y eficiente en nuestro hardware humilde:
1. **Eficiencia sobre potencia:** Utilizar unicamente los recursos necesarios para cada tarea, manteniendo el consumo ultra bajo para operar 24/7 de forma local.
2. **Latencia percibida cero:** El usuario nunca debe sentir que el sistema esta bloqueado. Mientras el LLM piensa, el sistema lanzara audios locales pregrabados ("Claro", "Dejame revisarlo") para ofrecer retroalimentacion instantanea.
3. **Maquina de Estados y Event Bus:** Todo el sistema opera bajo estados claros (IDLE, LISTENING, TRANSCRIBING, THINKING, EXECUTING, SPEAKING). Estos estados fluyen por nuestra conexion IPC, permitiendo que la interfaz visual, Discord y los modulos reaccionen de forma asincrona sin bloquear el bucle principal.
4. **Instrumentacion rigurosa:** Cada paso del pipeline (WakeWord, STT, LLM, TTS) mide y registra sus tiempos de ejecucion en milisegundos. Optimizamos con datos duros, no con intuiciones.
5. **Fallback Offline (LAN):** La arquitectura es agnostica de la red. Si el internet cae, Abril mantendra utilidades basicas (control domotico, reproduccion local, calendario) operando enteramente en la red local.


```mermaid
graph TD
    F1[Fase 1: Infraestructura y OS] --> F2[Fase 2: Red y SSH Headless]
    F2 --> F3[Fase 3: Entorno y Pipeline Principal]
    F3 --> F4[Fase 4: Audio y Wake Word Local]
    F4 --> F5[Fase 5: Conexion Nube Groq STT/LLM]
    F5 --> F6[Fase 6: Motor TTS Kokoro en Espanol]
    F6 --> F7[Fase 7: Memoria ChromaDB]
    F7 --> F8[Fase 8: Interfaz Visual mpv + IPC + X11]
    F8 --> F9[Fase 9: Bot de Discord]
    F9 --> F10[Fase 10: Orquestacion y Automatizacion]
    F10 --> F11[Fase 11: Microservicio Rust (Audio y Red)]
    F11 --> F12[Fase 12-14: Modulos Avanzados y Domotica]
    F12 --> F16[Fase 16-18: Integracion Final OpenClaw]
```

## Detalle de Fases y Tareas

### Fase 1: Infraestructura Fisica y Sistema Operativo
1. **Ensamblaje**: Instalar el SSD de 125 GB y conectar la mini pantalla HDMI a la GPU GTX 960.
2. **Instalacion de OS e Interfaz Ligera**: Instalar una distribución Linux base sin escritorio pesado (como **Ubuntu Server LTS** o **Debian**), pero anadiendo un servidor de ventanas minimalista (**X11 + Openbox**). Esto consume menos de 50MB de RAM y permite ejecutar reproductores de video graficos como `mpv`.
3. **Controladores Graficos**: Instalar los drivers propietarios de NVIDIA legacy de la serie **nvidia-driver-470** o **nvidia-driver-525** (segun la distro) en la GTX 960 para asegurar decodificacion acelerada por hardware de los videos.

### Fase 2: Red y Gestion Remota (Headless)
1. **Acceso Remoto**: Instalar y configurar el servidor OpenSSH.
2. **IP Estatica**: Configurar la tarjeta de red en `/etc/netplan/` o desde el router de tu casa para asignarle una IP estatica local (ej. `192.168.1.100`).
3. **Desconexion fisica**: Desconectar teclado, raton y monitor principal. A partir de aqui, controlaras todo por SSH desde tu laptop personal.

### Fase 3: Entorno Virtual y Dependencias de Python
1. **Dependencias del Sistema**: Instalar librerias esenciales para compilar y reproducir video/audio.
2. **Configuracion de Entorno**: Crear el directorio del proyecto y configurar el entorno virtual.
3. **Creacion de Archivos Base**: Inicializar `.env`, `config.json` y `requirements.txt`.

### Fase 4: Entrada de Audio y Wake Word Local
1. **Instalacion**: Instalar PyAudio y `openWakeWord`. *(Nota: La captura de audio crudo por PyAudio fue un dolor de cabeza de rendimiento, así que lo mandamos a Rust en la Fase 11)*.
2. **Configuracion ALSA**: Configurar los dispositivos de entrada de audio para asegurar que el microfono ambiental USB o Jack de 3.5mm sea el dispositivo de captura por defecto en Linux.
3. **Desarrollo de `wake_word.py`**:
   * Cargar el modelo pre-entrenado ONNX.
   * Monitorear el flujo del microfono (ahora alimentado por Rust).
   * Retornar una senal al Nerd (Python) cuando se detecte "Abril".

### Fase 4.5: Filtro de Audio de Entrada (Reduccion de Ruido)
1. **Reduccion de Ruido**: Dado que es un microfono ambiental de habitacion (sujeto a ruido de ventiladores, eco o musica), se integrara un filtro de procesamiento digital de senales (DSP).
2. **Implementacion**: Utilizar filtros nativos de PipeWire/PulseAudio o aplicar una biblioteca liviana en Python antes de enviar el buffer de audio a la API de Whisper en Groq. Esto previene transcripciones erroneas o alucinaciones debidas al ruido ambiente.

### Fase 5: Conexion Nube (Groq STT/LLM)
1. **Script `speech_to_text.py`**:
   * Al recibir la senal de activacion, graba el comando de audio del usuario en memoria o en un archivo temporal ligero.
   * Envia el audio a la API de Groq usando Whisper-large-v3 para obtener la transcripcion exacta en espanol en milisegundos.
2. **Script `brain_llm.py`**:
   * Envia la transcripcion junto con el historial reciente de conversacion a la API de Groq usando el modelo `llama3-8b-8192` (o superior).
   * Define el System Prompt para darle a Abril su personalidad unica, sus reglas de respuesta en espanol, y formateo adecuado para ser leido de forma natural.

### Fase 6: Sintesis de Voz Local con Kokoro-82M (Espanol Nativo)
1. **Instalacion**: Instalar Kokoro ONNX Runtime y dependencias de procesamiento de voz en espanol.
2. **Configuracion de Voz**:
   * Descargar el modelo `kokoro-v0_19.onnx` (~300MB) y los archivos JSON de fonemas en espanol.
   * Configurar el pipeline en el codigo de `text_to_speech.py` especificando el idioma espanol de forma explicita.
   * Cargar una voz en espanol compatible.

### Fase 7: Memoria a Largo Plazo con ChromaDB
1. **Instalacion**: Instalar `chromadb` y `sentence-transformers`.
2. **Estructura de `memory_system.py`**:
   * Inicializar una base de datos vectorial local.
   * Generar embeddings automaticos de cada conversacion relevante.
   * Al recibir una pregunta, buscar las 3 conversaciones pasadas mas semanticamente similares para inyectarlas como contexto en el prompt enviado a Groq.

### Fase 8: Interfaz Visual (mpv e IPC en Entorno Grafico Minimalista)
1. **Configuracion del Monitor**: Asegurar que la mini pantalla este configurada y detectada bajo la sesion de X11 en la salida HDMI.
2. **Configuracion de `mpv`**:
   * Lanzar una sesion ligera de Openbox para dar soporte grafico.
   * Crear un script en Bash que inicie `mpv` en modo pantalla completa en la pantalla secundaria bajo X11, levantando un servidor IPC.
3. **Controlador Visual (`visual_controller.py`)**:
   * Script en Python que se conecte al socket IPC.
   * Enviar comandos JSON para alternar videos de forma instantanea sin parpadeo de pantalla (Idle, Thinking, Speaking).

### Fase 9: Conexion con Discord
1. **Desarrollo del Bot**: Crear un bot en `discord-bot/bot.py` usando `discord.py`.
2. **Persistencia de Canal**: Vincular el bot a tus servidores/canales designados.
3. **Puente de Comunicacion**: Enlazar los mensajes de Discord con `brain_llm.py` y `memory_system.py`.

### Fase 10: Orquestacion, Arquitectura y Servicio (systemd)
1. **Bucle Principal e Instrumentacion (`main.py`)**: 
   * Construir el orquestador final midiendo los tiempos de cada modulo en milisegundos.
   * Implementar la maquina de estados completa (IDLE -> LISTENING -> TRANSCRIBING -> THINKING -> EXECUTING -> SPEAKING) que emita eventos por el socket IPC existente.
2. **Respuestas de Baja Latencia (Zero-Latency Fillers)**:
   * Extraer respuestas pregrabadas cortas y frases de personalidad a un archivo local de configuracion.
   * Reproducir instantaneamente frases de transicion ("Un segundo", "Voy con ello") antes de disparar las llamadas pesadas de STT/LLM a la red.
3. **Cola de Tareas y Modularidad**: Preparar la base para que futuras "skills" (domotica, clima) se encolen en un worker sin romper la respuesta del asistente.
4. **Servicio Automatico (systemd)**: Daemonizar el script para que arranque de forma silenciosa al encender la PC y se auto-recupere de caidas.

### Fase 10.5: Interrupcion por Voz (Barge-In)
1. **Logica de Interrupcion**: Habilitar que el usuario detenga a Abril mientras esta hablando si la respuesta es demasiado larga o incorrecta.
2. **Implementacion**: Mantener el hilo de `openWakeWord` en ejecucion y escuchando incluso en el estado `HABLANDO`.

---

## Modulos Avanzados (Interaccion de Ciencia Ficcion)

Para transformar a Abril de un asistente pasivo a uno proactivo y conectado con su entorno, se incorporaran estas funcionalidades:

### 1. El Exoesqueleto Rust (Fase 11 - Refactorizacion Hibrida)
Le clavamos Rust a la chingadera para que no tenga cuellos de botella en la escucha y el habla. Migracion del manejo de hardware a un microservicio en Rust para reducir el uso de CPU a 1% (o menos), siempre locuron.
* **Tecnologia**: Rust, cpal, rodio, y matemáticas puras para el VAD (RMS y Zero-Crossing Rate para los gordos números) en lugar de IA pesada.
* **Flujo**: El Exoesqueleto (Rust) captura el audio fisico y reproduce la voz sin congelar al Nerd (Python). Se comunican por sockets TCP locales.

### 2. Integracion de Hermes Agent (Fase 11C - Cerebro Persistente y Proactivo)
* **Tecnologia**: Hermes Agent (Nous Research), Gateway OpenAI-compatible en `http://127.0.0.1:8642/v1`.
* **Proposito**: Unificar la memoria episódica a largo plazo, el aprendizaje adaptativo del usuario, la proactividad (cron autónomo) y la mensajería omnicanal (Discord/Telegram) compartiendo el mismo contexto que el asistente de voz en la habitación.
* **Agnóstico a proveedores**: Configurado para correr con la clave y modelos de **Groq** por defecto, extensible en el futuro a modelos locales o remotos.

### 3. Dual Launcher: Version Servidor Consola vs Version Desktop GUI (Fase 12)
* **Modo Servidor / Consola Headless (Principal para Servidor Privado)**:
  * Ejecución 24/7 sin entorno gráfico pesado.
  * Interfaz de consola CLI interactiva e integración con servicios systemd/daemon.
  * Selector por flags o archivo de configuración para conmutar motor de agente (Abril Nativo vs Hermes Agent) y proveedor de tokens (Groq, OpenRouter, Ollama local, etc.).
* **Modo Desktop / Launcher de Escritorio**:
  * Ventana gráfica ligera (ej. Tauri o PySide minimalista).
  * Panel de configuración visual para seleccionar motor de agente (Abril Nativo vs Hermes Agent), proveedor de tokens activo (Groq, modelos locales Ollama/vLLM), testeo de audio y estado del servicio.

### 3. Control del Entorno (Fase 13 - Domotica Local)
* **Tecnologia**: `tinytuya` (para dispositivos Tuya/Smart Life).
* **Flujo**: *"Abril, apaga las luces"* -> Groq detecta la intencion -> Ejecuta la llamada local en milisegundos por Wi-Fi.

### 4. Personalizacion Dinamica del System Prompt (Fase 14)
* **Tecnologia**: Inyeccion dinamica de variables en `brain_llm.py`.
* **Ejemplo**: A partir de las 11:00 PM, el prompt le indicara a Abril: *"Es tarde en la noche. Responde con un tono suave y sugiere descanso"*.

### 5. Sistema de Alertas del Celular (Fase 15)
* **Tecnologia**: `KDE Connect` emparejado con tu dispositivo Android. Un script local lee las notificaciones entrantes y las filtra.
* **Caso de Uso**: Dejas tu celular cargando en otra habitacion o estas lejos del escritorio. Si recibes un mensaje urgente (ej. un WhatsApp de tu familia), Abril te interrumpe y dice: *"Muted, te acaba de llegar un mensaje de tu mama diciendo que ya llego"*. Te permite dictarle una respuesta en voz alta sin tocar tu telefono.


### 6. Integracion y Control de la PC Principal (Fase 16 - OpenClaw + MXC)
Habilidad de Abril para interactuar de manera remota con tu ordenador de uso diario y ejecutar tareas o automatizaciones complejas (abrir programas, revisar correos, organizar ventanas).
* **Tecnologia**: Framework **OpenClaw** y **Microsoft Execution Containers (MXC)**.
* **Implementacion**: Para usar las funciones de agente capaz de controlar tu PC, debes instalar OpenClaw y configurarlo exclusivamente en el PC que quieres usar para esto (NO en el hardware de Abril ni en la Raspberry Pi). Abril funcionara como orquestador central y enviara las instrucciones por red local a esa instancia de OpenClaw.
* **Seguridad**: Aprovechando los nuevos contenedores para agentes de Microsoft (MXC), OpenClaw correra en un entorno aislado (sandbox) en tu PC principal. Esto garantiza de manera nativa que si la IA llega a alucinar o intenta algo destructivo, el sistema operativo de Windows bloqueara la accion, protegiendo tus archivos.

### 7. Automatizacion Basada en Criterios de Presencia (Fase 17)
Dotar a la habitacion de sensores fisicos para que Abril reaccione a tu existencia sin necesidad de usar comandos de voz.
* **Tecnologia**: Integracion de sensores de presencia humana o de micromovimiento (PIR / Radar de microondas) conectados via Wi-Fi (ESP32 o Tuya).
* **Caso de Uso**: Llegas a tu cuarto despues del trabajo. El sensor detecta que entraste e instantaneamente Abril "despierta" su pantalla, enciende tus luces de ambiente led y te dice proactivamente: *"Hola Muted, bienvenido de nuevo"*. Si sales por mas de 15 minutos, ella misma apaga la iluminacion y la pantalla para mantener su bajo consumo.

### 8. Sincronizacion de Cuentas Personales (Fase 18)
Conectar el sistema principal de Abril a tus ecosistemas digitales privados de productividad.
* **Tecnologia**: Autenticacion ligera OAuth2 para integracion con APIs de Google Calendar, Gmail o Microsoft To-Do.
* **Caso de Uso**: Te despiertas y preguntas: *"Abril, ¿tengo algo importante hoy?"*. Ella lee tu calendario y responde: *"Tienes la entrega del proyecto a las 2 PM, y por cierto, te acaba de llegar un correo urgente de la universidad"*.

---

## Estimacion de Tiempos de Desarrollo

| Fase | Duracion Estimada | Dificultad |
| :--- | :--- | :--- |
| **Fase 1 y 2**: Montaje fisico, OS Linux Headless e IP estatica | 1 a 2 Semanas | Media |
| **Fase 3 y 4**: Entorno Python, Audio (ALSA) y Wake Word local | 2 a 3 Semanas | Alta |
| **Fase 4.5 a 6**: APIs de Groq, Filtros DSP y TTS Kokoro | 2 Semanas | Media |
| **Fase 7 y 8**: Memoria ChromaDB e Integracion IPC con `mpv` | 3 Semanas | Alta |
| **Fase 9 y 10**: Bot de Discord, Orquestador Principal y systemd | 2 Semanas | Media |
| **Fase 11 a 14**: Domotica, Celular y Proactividad | 1 a 2 Meses | Alta |
| **Fase 16 a 18**: OpenClaw, Sensores de Presencia y Cuentas | Varios Meses | Muy Alta |

---

## TO DO: Funcional Inmediato

Para que Abril pase a ser una asistente placentera de usar en el día a día, estas son las tareas prioritarias a pulir:

1. **Pulir Tiempos de Respuesta (Latencia End-to-End):**
   * **Streaming / Pipelining de oraciones hacia Rust:** No esperar a sintetizar toda la parrafada con Kokoro. Sintetizar la primera frase, mandarla al socket de audio en Rust para que empiece a sonar de al toque, y sintetizar las siguientes en segundo plano.
   * **Audios de relleno scripteados para reducir la sensacion de latencia:** Es casi inevitable tener latencia asi que mientras el LLM y la busqueda web procesan en paralelo, se reproducira un sonido breve o frase corta ("Un momento", "A ver") o sonidos de ambiente para pasar atenuar esa sensación.

2. **Pulir la Voz (Eliminar el sonido robótico):**
   * **Depuración de voces en Kokoro:** Probar combinaciones de voces (`ef_dora`, `em_alex`, `custom_blend.json`) y ajustar fonetización y velocidad.
   * **Evaluación de Piper TTS:** Evaluar como alternativa ultraliviana Piper TTS con voces neuronales en español (latinoamericano / España) de alta naturalidad y bajo consumo de CPU.

3. **Avatar y Presencia Visual:**
   * **Sincronización completa con IPC:** Conectar el visualizador de estados (IDLE, LISTENING, THINKING, HABLANDO) con el bucle real en vivo.
   * **Modo dual:** Visualizador ASCII en consola para el modo servidor headless y reproductor de video en pantalla secundaria dedicada con `mpv` bajo X11.

4. **Integración con OpenClaw (Control de la PC Principal):**
   * Configurar la comunicación entre el servidor de Abril (servidor privado / Raspberry Pi) y la PC principal de Muted. (o la tuya)
   * Ejecutar tareas del ordenador diario (abrir programas, revisar correos, automatizaciones) aisladas en contenedores seguros MXC.

5. **Discord (Unificación de Telepatía):**
   * Unificar el bot de Discord con el nuevo orquestador y la memoria de ChromaDB / Hermes para que hablar por Discord use el mismo cerebro que hablar en la habitación.

6. **Domótica Local:**
   * Conectar `backend/domotica.py` con `tinytuya` para que Abril pueda apagar o encender las luces de la habitación mediante Function Calling por voz (*"Abril, apaga las luces"*).

7. **Dual Launcher:**
   * **Modo Servidor / Consola Headless (24/7):** Versión ligera sin interfaz gráfica para correr de forma perpetua en el servidor privado de Muted. Permite configurar la capa de agente (Abril Nativo o Hermes Agent) y el proveedor del modelo (Groq, Ollama local, etc.).
   * **Modo Desktop GUI:** Launcher gráfico con selector visual para conmutar entre orquestadores (Abril Nativo vs Hermes Agent), proveedores de modelo (Groq, Ollama/vLLM local) y monitoreo de periféricos.
