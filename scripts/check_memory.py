import chromadb

def check():
    c = chromadb.PersistentClient("data/chromadb")
    col = c.get_collection("abril_memories")
    data = col.get()
    docs = data.get("documents", [])
    metas = data.get("metadatas", [])
    ids = data.get("ids", [])
    print(f"Total recuerdos en BD: {len(docs)}")
    for i, (d, m, mid) in enumerate(zip(docs, metas, ids)):
        ctx = m.get("context", "desconocido")
        ts = m.get("timestamp", "")
        # limpiar caracteres conflictivos para consola
        safe_text = d.replace("\n", " ")[:100]
        print(f"[{i+1}] ({ctx} | {ts[:19]}) {safe_text}")

if __name__ == "__main__":
    check()
