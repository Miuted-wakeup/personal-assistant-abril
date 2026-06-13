import urllib.request
import os
import shutil
from pathlib import Path

def download_file(url, filepath):
    print(f"Descargando {os.path.basename(filepath)}... (esto puede tardar unos minutos)")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Descarga completada: {filepath}")
    except Exception as e:
        print(f"❌ Error descargando {filepath}: {e}")

def main():
    print("=== Configurando Entorno de Abril ===\n")
    
    # 1. Crear .env si no existe
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if not env_path.exists():
        if env_example.exists():
            shutil.copy(env_example, env_path)
            print("✅ Archivo .env creado a partir de .env.example.")
            print("⚠️ IMPORTANTE: Abre el archivo .env y coloca tus API Keys antes de continuar.\n")
        else:
            print("⚠️ No se encontró .env.example para crear la plantilla.\n")
    else:
        print("✅ Archivo .env ya existe.\n")
        
    # 2. Crear carpetas necesarias
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # 3. Descargar modelos de voz de Kokoro
    urls = {
        "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
        "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
    }
    
    for filename, url in urls.items():
        file_path = assets_dir / filename
        if not file_path.exists():
            download_file(url, file_path)
        else:
            print(f"✅ Archivo {filename} ya existe en /assets.")
            
    print("\n🎉 ¡Todo listo!")
    print("Para iniciar a Abril en Discord, corre: python discord-bot/bot.py")

if __name__ == "__main__":
    main()
