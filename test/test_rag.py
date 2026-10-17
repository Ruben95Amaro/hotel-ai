from app.services.document_service import DocumentService
from app.services.rag_service import RAGService


document_service = DocumentService()
rag_service = RAGService()



document_path = "data/hotel.txt"

text = document_service.load_document(
    str(document_path)
)

chunks = document_service.split_into_chunks(text)

print(f"Loaded {len(chunks)} chunks.")

rag_service.add_chunks(chunks)

print("Chunks added to ChromaDB.")

query = "What time is check-in?"

results = rag_service.search(
    query=query,
    limit=3,
)

print(f"\nQuery: {query}")

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print(result)