#!/bin/bash
# Script de arranque del sistema (X11 + mpv)

echo "Preparando el entorno visual..."

# Iniciar reproductor de video (mpv) en background levantando el servidor IPC
# Se asume que Openbox o el entorno X11 ya está corriendo en DISPLAY=:0
DISPLAY=:0 mpv --fullscreen --screen=1 --loop-file=inf --input-ipc-server=/tmp/mpv-socket assets/videos/idle.mp4 &
MPV_PID=$!

echo "Reproductor MPV iniciado (PID: $MPV_PID)."

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Advertencia: No se encontró el entorno virtual 'venv'."
fi

echo "Iniciando el backend de Abril..."
# Iniciar orquestador principal
python3 backend/main.py

# Limpieza al salir
echo "Cerrando sistema..."
kill $MPV_PID
