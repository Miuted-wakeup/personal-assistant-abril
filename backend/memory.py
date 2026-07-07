import os
import uuid
import chromadb
from datetime import datetime
from chromadb.config import Settings
from backend.logger import setup_logger

logger = setup_logger("Memory")

class MemoryManager:
    def __init__(self, data_dir="data/chromadb"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"iniciando gestor de memoria (chromadb) en {self.data_dir}")
        try:
            # cliente local persistente
            self.client = chromadb.PersistentClient(path=self.data_dir)
            # crear o obtener la coleccion de recuerdos de abril
            self.collection = self.client.get_or_create_collection(
                name="abril_memories",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("memoria cargada correctamente")
        except Exception as e:
            logger.error(f"error iniciando chromadb: {e}")
            self.client = None
            self.collection = None

    def add_memory(self, user, context, text):
        """
        Guarda un nuevo recuerdo en la base de datos vectorial.
        """
        if not self.collection:
            return False
            
        try:
            timestamp = datetime.now().isoformat()
            memory_id = f"mem_{uuid.uuid4().hex[:10]}"
            
            # almacenamos el texto original como el documento a vectorizar
            # y los metadatos para filtrado
            self.collection.add(
                documents=[text],
                metadatas=[{"user": user, "context": context, "timestamp": timestamp}],
                ids=[memory_id]
            )
            logger.debug(f"recuerdo guardado para {user}: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"error guardando recuerdo: {e}")
            return False

    def query_memory(self, user, query_text, n_results=3):
        """
        Busca recuerdos relevantes al texto de entrada.
        """
        if not self.collection:
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"user": user} # Solo busca recuerdos de este usuario
            )
            
            # Formateamos los resultados para que sean fáciles de usar por el LLM
            memories = []
            if results and results.get('documents') and len(results['documents']) > 0:
                docs = results['documents'][0]
                metas = results['metadatas'][0]
                
                for doc, meta in zip(docs, metas):
                    timestamp_str = meta.get("timestamp", "")
                    contexto = meta.get("context", "general")
                    
                    # Convertir a tiempo relativo para ayudar al LLM (que es pequeño) a entender los tiempos
                    try:
                        mem_date = datetime.fromisoformat(timestamp_str)
                        now = datetime.now()
                        dias_dif = (now.date() - mem_date.date()).days
                        hora_str = mem_date.strftime("%H:%M")
                        
                        if dias_dif == 0:
                            tiempo_relativo = f"Hoy a las {hora_str}"
                        elif dias_dif == 1:
                            tiempo_relativo = f"Ayer a las {hora_str}"
                        else:
                            tiempo_relativo = f"Hace {dias_dif} días"
                    except Exception:
                        tiempo_relativo = timestamp_str.replace("T", " ")[:16]

                    # TRUCO ANTILORO: Ocultarle a la IA lo que ella misma respondió en el pasado, 
                    # para que no lo copie y pegue textualmente.
                    doc_user_only = doc.split('\nAbril:')[0]

                    memories.append(f"[{tiempo_relativo} | {contexto}] {doc_user_only}")
                    
            logger.debug(f"se encontraron {len(memories)} recuerdos relevantes para '{query_text[:20]}'")
            return memories
        except Exception as e:
            logger.error(f"error consultando memoria: {e}")
            return []
