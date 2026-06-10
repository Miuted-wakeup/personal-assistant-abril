# Recursos Multimedia (Assets)

Directorio para los elementos estaticos que no son codigo fuente.

## Estructura

- `videos/`: Contiene los clips de video utilizados para dar retroalimentacion visual en la mini pantalla.
  - `idle.mp4`: Loop de respiracion o inactividad.
  - `thinking.mp4`: Animacion de atencion mientras se procesan datos en la nube.
  - `speaking.mp4`: Animacion de movimiento de labios.
- `voices/`: Modelos de voz, tensores o configuraciones especiales (`custom_blend.json`) utilizados por el motor TTS (Kokoro).

**Nota**: Los archivos excesivamente pesados o modelos ONNX de gran formato deben ser gestionados localmente y no subirse al sistema de control de versiones.
