
from pathlib import Path

from app.services.document_service import DocumentService
from app.services.rag_service import RAGService


document_service = DocumentService()
rag_service = RAGService()

project_root = Path(__file__).resolve().parent.parent
document_path = project_root / "data" / "hotel.txt"

text = document_service.load_document(str(document_path))
chunks = document_service.split_into_chunks(text)

rag_service.add_chunks(chunks)

queries = [
    "What time is check-in?",
    "Does the hotel have a casino?",
]

for query in queries:
    results = rag_service.search(query=query, limit=3)

    print(f"\nQuestion: {query}")

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Distance: {result['distance']}")
        print(result["document"])
