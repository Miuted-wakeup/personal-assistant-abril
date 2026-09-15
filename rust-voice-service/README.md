# Rust Voice Service

Este modulo nacio de la necesidad de ahorrar recursos. Aunque actualmente el proyecto se esta estructurando sobre este PC humilde, la meta es que Abril pueda correr en una Raspberry Pi 24/7 sin derretirla. Python es excelente como orquestador logico (para hablar con la IA), pero es muy lento y bloqueante para manejar hardware de audio crudo en tiempo real.

Para eso esta Rust. Este microservicio actua como el puente directo entre el hardware (microfono y altavoces) y Python.

## Arquitectura Hibrida

1. **Salida de Audio (Altavoces):** Python sintetiza la voz con Kokoro y le tira el archivo WAV por red interna (TCP 9001) a Rust. Rust lo reproduce de forma asincrona usando `cpal` y `rodio`. Esto evita que el orquestador de Python se quede bloqueado esperando a que termine el audio.
2. **Entrada de Audio (Microfono):** Rust escucha el microfono 24/7. En lugar de utilizar pesados modelos de Inteligencia Artificial (como ONNX) para saber si estas hablando, utiliza algoritmos matematicos puros de procesamiento de senales (DSP). Calculando la energia (Root Mean Square - RMS) y la tasa de cruce por cero (o Zero-Crossing Rate si sos un gordo numeros) del audio en bruto, determina si hay voz humana. Si detecta habla, transmite el audio a Python por TCP. Si hay silencio, descarta los datos de inmediato, salvando casi el 100% de la CPU.
3. **Discord Voice (A futuro):** Rust se encargara del trafico UDP encriptado de Discord, aislando a Python de los problemas de latencia de red.

## Compilacion y Pruebas

Para compilar el servicio, necesitas el toolchain de Rust.

### En Linux (Objetivo Final)
La compilacion en Linux es la mas estable y facil. Solo asegurate de tener las dependencias de sonido ALSA instaladas:
```bash
sudo apt install build-essential libasound2-dev
cargo run --release
```

### En Windows (Entorno de Desarrollo)
Windows Defender suele bloquear los archivos intermedios de compilacion de Rust (lanzando un `os error 32`). Para desarrollar localmente sin problemas:

1. Agrega la carpeta `rust-voice-service\target` a las exclusiones de Windows Defender.
2. Asegurate de estar usando el toolchain nativo de MSVC en lugar de GNU:
   ```bash
   rustup default stable-msvc
   ```
3. Ejecuta el servidor:
   ```bash
   cargo run
   ```

Una vez que la consola confirme:
- `Audio de salida listo. Escuchando peticiones WAV en 127.0.0.1:9001...`
- `Stream de micrófono listo. Transmitiendo audio activo en 127.0.0.1:9002...`

Puedes ejecutar el backend de Python (`backend/wake_word.py` o `backend/main.py`), el cual se conectará automáticamente a los puertos locales de Rust sin congelar la CPU ni depender de PyAudio.
