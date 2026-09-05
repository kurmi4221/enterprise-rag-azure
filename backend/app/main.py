from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.app.services.rag_service import ask_rag

try:
    from .core.logging import configure_logging
    from .core.middleware import CorrelationIdMiddleware
except ImportError:  # pragma: no cover
    from backend.app.core.logging import configure_logging
    from backend.app.core.middleware import CorrelationIdMiddleware

# ---------------------------------------------------------

# Logging

# ---------------------------------------------------------

configure_logging()

# ---------------------------------------------------------

# FastAPI application

# ---------------------------------------------------------

app = FastAPI(
title="Enterprise RAG API",
version="0.1.0",
)

# ---------------------------------------------------------

# Middleware

# ---------------------------------------------------------

app.add_middleware(
CorrelationIdMiddleware
)

# ---------------------------------------------------------

# Request models

# ---------------------------------------------------------

class ChatRequest(BaseModel):
    question: str

# ---------------------------------------------------------

# Health check

# ---------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
            "service": "enterprise-rag-api",
        }   

# ---------------------------------------------------------

# Readiness check

# ---------------------------------------------------------

@app.get("/ready")
async def readiness():
    return {
        "status": "ready",
            }

# ---------------------------------------------------------

# Chat endpoint

# ---------------------------------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):
    result = ask_rag(
            request.question
                    )

    return result

# ---------------------------------------------------------

# Document upload endpoint

# ---------------------------------------------------------

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    raise HTTPException(
        status_code=501,
        detail="Document upload and ingestion are not implemented yet",
    )