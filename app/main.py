"""College Helpdesk Chatbot — FastAPI app."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .rag import KnowledgeBase
from .schemas import AddDocRequest, AskRequest, AskResponse, DocInfo

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="College Helpdesk Chatbot", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

kb = KnowledgeBase()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "documents": len(kb.doc_list()), "chunks": len(kb.chunks)}


@app.get("/documents", response_model=list[DocInfo])
def list_docs() -> list[dict]:
    return kb.doc_list()


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    answer, sources = kb.ask(req.question.strip(), top_k=req.top_k)
    return AskResponse(answer=answer, sources=sources)


@app.post("/documents")
def add_doc(req: AddDocRequest) -> dict:
    filename = kb.add_document(req.title, req.content)
    return {"source": filename, "documents": len(kb.doc_list())}
