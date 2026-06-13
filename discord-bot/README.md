# Bot de Discord

Este modulo aloja la interfaz de conexion entre Discord y el "cerebro" de Abril.

## Funcionamiento

- Utiliza `discord.py` para leer mensajes de servidores y mensajes directos (MD/DM).
- Implementa filtros para ignorar mensajes de otros bots (evitando loops infinitos).
- Ejecuta las llamadas al LLM en hilos asíncronos (`asyncio.to_thread`) para evitar bloquear el event loop de Discord.
- `bot.py` procesa la entrada, limpia las menciones y la envía directamente a la clase `BrainLLM` del backend.
- Dado que comparten la misma instancia, las interacciones en Discord alteran el historial de memoria de la misma forma que lo harían las interacciones por voz.
- **Preparación de Voz:** Se ha implementado el soporte `discord.py[voice]` y `PyNaCl` en las dependencias para futuras fases donde el bot transmita el audio de Kokoro directamente a los canales de voz.

## Configuración
Requiere que `DISCORD_TOKEN` esté configurado en el archivo `.env` de la raíz del proyecto.
Para que el bot pueda leer los mensajes, es obligatorio encender el **Message Content Intent** en el portal de desarrolladores de Discord.
