import os
import sys
import chromadb
from datetime import datetime

# Agregar la ruta base para imports si es necesario
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def ver_memoria():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chromadb")
    
    if not os.path.exists(data_dir):
        print("Error: No se encontró la base de datos ChromaDB. Asegúrate de que Abril haya guardado algún recuerdo.")
        return
        
    print("Conectando al hipocampo (ChromaDB) de Abril...")
    try:
        client = chromadb.PersistentClient(path=data_dir)
        collection = client.get_collection(name="abril_memories")
        
        datos = collection.get()
        ids = datos.get("ids", [])
        documents = datos.get("documents", [])
        metadatas = datos.get("metadatas", [])
        
        if not ids:
            print("La memoria está vacía.")
            return
            
        print(f"\nSe encontraron {len(ids)} recuerdos almacenados:\n")
        print("="*60)
        
        for idx in range(len(ids)):
            mem_id = ids[idx]
            doc = documents[idx]
            meta = metadatas[idx]
            
            user = meta.get("user", "desconocido")
            timestamp = meta.get("timestamp", "")
            context = meta.get("context", "general")
            
            # Limpiar timestamp para visualización
            ts_str = timestamp.replace("T", " ")[:19] if timestamp else "Desconocido"
            
            print(f"ID: {mem_id}")
            print(f"Usuario: {user}")
            print(f"Fecha/Hora: {ts_str}")
            print(f"Contexto: {context}")
            print("-" * 60)
            print(f"RECUERDO:")
            for line in doc.split('\n'):
                print(f"   {line}")
            print("="*60)
            
    except Exception as e:
        print(f"Error al leer la memoria: {e}")

if __name__ == "__main__":
    ver_memoria()
