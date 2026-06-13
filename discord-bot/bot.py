import os
import sys
import asyncio
import discord

# agrega backend al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger
from backend.config import DISCORD_TOKEN
from backend.brain_llm import BrainLLM

logger = setup_logger("DiscordBot")

class AbrilDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = BrainLLM()
        
    async def on_ready(self):
        logger.info(f"Conectada a Discord como {self.user}!")
        
        # Configurar un estado o "Actividad" personalizada para Abril
        actividad = discord.Activity(type=discord.ActivityType.watching, name="tus comandos 👁️")
        await self.change_presence(status=discord.Status.online, activity=actividad)
        
    async def on_message(self, message):
        # Ignorar mensajes de otros bots o de sí misma
        if message.author.bot:
            return
            
        # Responder solo si la mencionan o si es un Mensaje Directo (DM)
        if self.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            logger.info(f"Mensaje recibido de {message.author.name}")
            
            # Limpiar mención para que el LLM solo vea el texto real
            prompt = message.clean_content.replace(f"@{self.user.name}", "").strip()
            
            # Mostrar "Abril está escribiendo..."
            async with message.channel.typing():
                # Ejecutamos el LLM en un hilo separado para no congelar el bot de Discord
                respuesta = await asyncio.to_thread(self.llm.generate_response, prompt, message.author.name)
                
                # Enviar respuesta
                await message.reply(respuesta)

def run_bot():
    logger.info("Iniciando bot de discord...")
    if not DISCORD_TOKEN or DISCORD_TOKEN == "tu_token":
        logger.error("¡Falta el token de Discord en el archivo .env (DISCORD_TOKEN)!")
        return
        
    # Activar intents para poder leer el contenido de los mensajes
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = AbrilDiscordBot(intents=intents)
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bot()
