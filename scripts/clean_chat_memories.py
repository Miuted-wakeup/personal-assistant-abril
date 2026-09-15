import chromadb

def clean_chat_memories():
    c = chromadb.PersistentClient("data/chromadb")
    col = c.get_collection("abril_memories")
    data = col.get()
    
    docs = data.get("documents", [])
    metas = data.get("metadatas", [])
    ids = data.get("ids", [])
    
    chat_ids = []
    kept_count = 0
    for doc, meta, mid in zip(docs, metas, ids):
        ctx = meta.get("context", "")
        if ctx == "chat":
            chat_ids.append(mid)
        else:
            kept_count += 1
            print(f"Conservando recuerdo permanente [{ctx}]: {doc}")
            
    if chat_ids:
        print(f"\nEliminando {len(chat_ids)} recuerdos obsoletos de tipo 'chat'...")
        col.delete(ids=chat_ids)
        print("Limpieza completada exitosamente.")
    else:
        print("No se encontraron recuerdos de tipo 'chat'.")
        
    print(f"Total recuerdos restantes en la base de datos: {col.count()}")

if __name__ == "__main__":
    clean_chat_memories()
