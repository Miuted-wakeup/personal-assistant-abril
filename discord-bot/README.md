# Bot de Discord

Este modulo aloja la interfaz de conexion entre Discord y el "cerebro" de Abril.

## Funcionamiento

- Utiliza `discord.py` para leer mensajes de servidores y canales especificos.
- `bot.py` procesa la entrada, y la envia directamente a la clase `BrainLLM` del backend.
- Dado que comparten la misma instancia (o memoria vectorial externa), las interacciones en Discord alteran el historial de memoria de la misma forma que lo harian las interacciones por voz.

## Configuracion
Requiere que `DISCORD_TOKEN` este configurado en el archivo `.env` de la raiz del proyecto.
