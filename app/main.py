import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.chat import router as chat_router

print("Initializing FastAPI app")


app = FastAPI(
    title="Hotel AI Assistant",
    version="1.0.0"
)

app.include_router(chat_router)


@app.get("/")
def redirect_to_endpoint():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}