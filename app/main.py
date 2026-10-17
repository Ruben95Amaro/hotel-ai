
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.chat import router as chat_router, rag_service
from app.services.document_service import DocumentService


PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOTEL_DOCUMENT = PROJECT_ROOT / "data" / "hotel.txt"

app = FastAPI(
    title="Hotel AI Assistant",
    version="1.0.0",
)

app.include_router(chat_router)


@app.on_event("startup")
def ingest_hotel_document() -> None:
    if not HOTEL_DOCUMENT.is_file():
        raise FileNotFoundError(
            f"Hotel document not found: {HOTEL_DOCUMENT}"
        )

    document_service = DocumentService()
    text = document_service.load_document(str(HOTEL_DOCUMENT))
    chunks = document_service.split_into_chunks(text)

    if not chunks:
        raise RuntimeError("The hotel document contains no chunks.")

    rag_service.add_chunks(chunks)

    print(
        f"Hotel document ingested: {len(chunks)} chunks. "
        f"ChromaDB: {rag_service.collection.count()} documents.",
        flush=True,
    )


@app.get("/")
def redirect_to_endpoint():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok"}
