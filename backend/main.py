from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import os
import uuid
from sqlalchemy import text

from backend.rag.ingest import process_file
from backend.rag.agent.graph import process_chat
from backend.config import ALLOWED_ORIGINS
from backend.database import SessionLocal, DocChunk, init_db

app = FastAPI(title="RAG Chatbot Workshop")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_user"
    mode: str = "auto"
    top_k: int = 5


@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "db": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database check failed: {exc}")
    finally:
        db.close()

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer, citations, trace = process_chat(request.message, request.mode)
        return {
            "answer_text": answer,
            "citations": citations,
            "tool_trace": trace,
            "latency_ms": 10
        }
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
            return JSONResponse(
                status_code=503,
                content={"error": "Gemini API quota exceeded. Please wait a minute and try again, or use a different API key.", "detail": err_str[:200]}
            )
        raise HTTPException(status_code=500, detail=f"Chat processing error: {err_str[:300]}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    # This will stream responses
    async def event_generator():
        yield {"data": f"Receiving streaming chunk for {request.message}...\n\n"}
    
    return EventSourceResponse(event_generator())

@app.get("/documents")
def list_documents():
    """List all unique documents that have been ingested."""
    db = SessionLocal()
    try:
        rows = db.execute(text(
            "SELECT DISTINCT doc_id, metadata->>'filename' AS filename, COUNT(*) AS chunks "
            "FROM doc_chunks GROUP BY doc_id, filename ORDER BY filename"
        )).fetchall()
        return [{"doc_id": r.doc_id, "filename": r.filename or "Unknown", "chunks": r.chunks} for r in rows]
    finally:
        db.close()

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete all chunks for a given document."""
    db = SessionLocal()
    try:
        db.query(DocChunk).filter(DocChunk.doc_id == doc_id).delete()
        db.commit()
        return {"status": "deleted", "doc_id": doc_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/ingest/file")
async def ingest_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_id: str = Form(None),
    chunk_size: int = Form(600),
    overlap: int = Form(100)
):
    from backend.config import UPLOAD_DIR
    
    if doc_id is None:
        doc_id = str(uuid.uuid4())
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    # Process asynchronously
    background_tasks.add_task(process_file, file_path, doc_id, chunk_size, overlap)
    
    return {"status": "processing", "doc_id": doc_id, "filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),
        reload=True,
    )
