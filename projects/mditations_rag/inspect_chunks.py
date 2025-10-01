from vector_store import VectorStore


def main():
    store = VectorStore()
    # Get all documents in the collection
    results = store.collection.get()
    docs = results.get("documents", []) or []
    metadatas = results.get("metadatas", []) or []
    print(f"Total chunks: {len(docs)}")
    for i, (doc, meta) in enumerate(zip(docs, metadatas)):
        print(f"\n--- Chunk {i} ---")
        print(f"Metadata: {meta}")
        print(f"Content: {doc[:500]}...")  # Print first 500 chars for brevity

if __name__ == "__main__":
    main() 