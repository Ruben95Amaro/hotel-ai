from pathlib import Path

from app.services.document_service import DocumentService


document_service = DocumentService()

document_path = "data/hotel.txt"

text = document_service.load_document(
    str(document_path)
)

chunks = document_service.split_into_chunks(text)

print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks):
    print(f"\n--- Chunk {index} ---")
    print(chunk)