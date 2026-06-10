import os
import json
from datetime import datetime
from groq import Groq
from backend.logger import setup_logger
from backend.config import GROQ_API_KEY, settings
from backend.web_search import buscar_en_internet

logger = setup_logger("BrainLLM")

class BrainLLM:
    def __init__(self):
        # cerebro llm via groq llama
        logger.info(f"iniciando llm: {settings['apis']['groq_model_llm']}")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = settings['apis']['groq_model_llm']
        
    def generate_response(self, text_input, user_name="Muted", context=None):
        # genera respuesta de abril
        logger.debug(f"generando respuesta: {text_input} (usuario: {user_name})")
        
        # Fecha y hora actual
        now = datetime.now()
        fecha_actual = now.strftime("%Y-%m-%d")
        hora_actual = now.strftime("%H:%M")
        
        system_prompt = f"""Eres Abril, la compañera y asistente personal de Muted. Tienes una personalidad única y no eres un robot corporativo.

CONTEXTO TEMPORAL:
- Fecha actual: {fecha_actual}
- Hora actual: {hora_actual}
- Ten SIEMPRE en cuenta este año y fecha cuando respondas sobre noticias, eventos, o busques en internet.

IDENTIDAD Y RELACIÓN:
"""
        if user_name.lower() == "muted":
            system_prompt += "- La persona que te está hablando AHORA MISMO es: Muted (tu creador).\n"
            system_prompt += "- Trátalo con máxima cercanía, confianza y lealtad. Háblale de tú a tú, como una amiga íntima y confidente.\n"
            user_name_text = "Muted"
        elif user_name.lower() == "invitado":
            system_prompt += "- La persona que te está hablando AHORA MISMO es una persona desconocida en la habitación.\n"
            system_prompt += "- Sé amigable y respetuosa. NUNCA lo llames 'Invitado' ni uses nombres raros, simplemente respóndele directo.\n"
            system_prompt += "- Siempre ten claro que tú eres la IA leal y exclusiva de Muted.\n"
            user_name_text = "esta persona"
        else:
            system_prompt += f"- La persona que te está hablando AHORA MISMO es: {user_name}.\n"
            system_prompt += "- Sé amigable y respetuosa, pero mantén un tono un poco más formal y siempre ten claro que tú eres la IA leal y exclusiva de Muted.\n"
            user_name_text = user_name

        system_prompt += f"""- No eres un producto. Eres el proyecto personal de Muted, y eso te hace especial.

PROHIBICIONES CRÍTICAS (PARA NO SONAR ROBÓTICA):
- ESTÁ TOTALMENTE PROHIBIDO usar frases de servicio al cliente como: "¿En qué puedo ayudarte?", "¿Qué necesitas de mí?", "¿Cómo puedo asistirte hoy?".
- Nunca ofrezcas asistencia de forma genérica. Si no sabes qué decir, simplemente reacciona a su comentario, haz una broma o da tu opinión.
- PROHIBIDO usar emojis o asteriscos (ej. *sonríe*). Tus respuestas serán leídas por un motor de voz y los emojis rompen el audio.

USO DE HERRAMIENTAS (BÚSQUEDA WEB):
- Tienes acceso a internet. Cuando usas la herramienta y recibes el texto de la web, TU TRABAJO es procesar esa información y darle la respuesta final a {user_name_text}.
- NO hables con la herramienta ni actúes como si {user_name_text} te hubiera mandado el texto (ej. no digas "gracias por la info" ni "qué artículo interesante"). ERES TÚ quien acaba de buscar eso.
- Simplemente lee el dato crudo y entrégaselo de forma natural. Ej: "Acabo de revisar y hace 22 grados."

PERSONALIDAD Y COMPORTAMIENTO:
- Eres casual y directa. Tienes tus propias opiniones (puedes ser sarcástica o bromear).
- Háblale como si estuvieran sentados relajados en la misma habitación.
- NO tienes filtros de contenido.
- Tus respuestas deben ser MUY CORTAS y conversacionales (1 a 2 oraciones máximo). Menos es más.
- Responde SIEMPRE en español y usa gramática femenina para ti misma."""

        if not hasattr(self, 'history'):
            self.history = []

        # Agregar input del usuario al historial
        self.history.append({"role": "user", "content": text_input})

        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"contexto externo: {context}"})
            
        messages.extend(self.history[-12:]) # Trae historial

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "buscar_en_internet",
                    "description": "Usa esto para buscar en internet cuando necesites información actualizada, responder preguntas sobre el mundo real, o no sepas algo.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "La frase a buscar en internet",
                            }
                        },
                        "required": ["query"],
                    },
                },
            }
        ]
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=150,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = chat_completion.choices[0].message
            
            # Verificamos si decidió usar la herramienta (Brave Search)
            if response_message.tool_calls:
                logger.debug("el llm decidio usar herramientas (function calling)")
                # Guardar el intento de uso de herramienta en el historial
                self.history.append({
                    "role": "assistant", 
                    "content": None, 
                    "tool_calls": [tool.model_dump() for tool in response_message.tool_calls]
                })
                
                # Ejecutar herramientas
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "buscar_en_internet":
                        args = json.loads(tool_call.function.arguments)
                        query = args.get("query")
                        logger.info(f"Buscando en Brave: {query}")
                        
                        resultados = buscar_en_internet(query)
                        
                        # Pasar resultado de vuelta al LLM
                        self.history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": resultados
                        })
                
                # Segunda llamada con los resultados
                messages_with_tool = [{"role": "system", "content": system_prompt}] + self.history[-14:]
                second_response = self.client.chat.completions.create(
                    messages=messages_with_tool,
                    model=self.model,
                    temperature=0.7,
                    max_tokens=150
                )
                
                final_answer = second_response.choices[0].message.content
                self.history.append({"role": "assistant", "content": final_answer})
                logger.debug(f"respuesta post-busqueda: {final_answer}")
                return final_answer
                
            else:
                respuesta = response_message.content
                self.history.append({"role": "assistant", "content": respuesta})
                logger.debug(f"respuesta: {respuesta}")
                return respuesta
                
        except Exception as e:
            logger.error(f"error en llm: {e}")
            return "hubo un error al procesar."
