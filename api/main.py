from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import tempfile, os, filetype
from dotenv import load_dotenv

load_dotenv()

from core.extractor import extract
from core.chunker import chunk_text
from core.embedder import embed
from core.vector_store import insert_chunks
from agent.supervisor import run_supervisor

app = FastAPI(title="ProductMind API", version="1.0.0")

class QueryRequest(BaseModel):
    query: str

class LoadURLRequest(BaseModel):
    url: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/query")
async def query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = run_supervisor(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/load/url")
async def load_url(request: LoadURLRequest):
    try:
        text = extract(request.url, "url")
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from URL.")
        chunks = chunk_text(text)
        embeddings = embed(chunks)
        insert_chunks(chunks, embeddings, source=request.url)
        return {"status": "ok", "source": request.url, "chunks_stored": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load/file")
async def load_file(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        kind = filetype.guess(file_bytes)
        if kind is None:
            raise HTTPException(status_code=400, detail="Cannot detect file type.")
        if kind.mime == "application/pdf":
            source_type = "pdf"
        elif kind.mime.startswith("image/"):
            source_type = "image"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {kind.mime}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{kind.extension}") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        text = extract(tmp_path, source_type)
        os.unlink(tmp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from file.")
        chunks = chunk_text(text)
        embeddings = embed(chunks)
        insert_chunks(chunks, embeddings, source=file.filename)
        return {"status": "ok", "source": file.filename, "chunks_stored": len(chunks)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))