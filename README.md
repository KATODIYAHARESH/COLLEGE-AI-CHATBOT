# College Helpdesk Chatbot (RAG)

A question-answering chatbot over a college's own documents. Ask about
admissions, exams, hostel, library, fees, or scholarships — and get an
answer **grounded in the documents**, with source citations, not a
made-up reply.

This is retrieval-augmented generation (RAG) in its simplest honest
form: TF-IDF retrieval over local Markdown documents, no external API
and no API key needed. Everything runs offline.

## How it works

```
Question → TF-IDF vector → cosine similarity → top matching chunks
        → answer built from those chunks, each cited by source file
```

- If no chunk matches well enough, the bot says so instead of guessing.
- Add a document and the index rebuilds immediately — no restart needed.

## Features

- Ask questions in plain language, get cited answers
- Source citations on every answer (which document it came from)
- Add new documents through the API — the knowledge base grows live
- "I don't know" fallback instead of hallucinated answers
- Plain HTML/CSS/JS chat frontend — no build step

## Quick start

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
uvicorn app.main:app --reload --port 8000
```

Open http://127.0.0.1:8000 in your browser.

## Try it

- "What are the library hours?"
- "How do I apply for a scholarship?"
- "What documents are needed for admission?"

## API

### `GET /health`

```json
{"status": "ok"}
```

### `GET /documents`

Lists the knowledge-base documents and how many chunks each has.

### `POST /ask`

Request:

```json
{"question": "What are the library hours?", "top_k": 3}
```

Response:

```json
{
  "answer": "Based on the college documents:\n\n...",
  "sources": [{"source": "library.md", "score": 0.62}]
}
```

### `POST /documents`

Add a document to the knowledge base:

```json
{"title": "Sports", "content": "The annual sports meet is held in..."}
```

## Make it yours

The files in `app/kb/` are **sample** documents with generic content.
Replace them with your own college's real notices, circulars, and
rulebooks (as `.md` files) and the bot answers from those instead.
No code changes needed.

Want LLM-polished answers later? The retrieval layer (`app/rag.py`)
already returns ranked chunks — pass them to any chat model as context.
That upgrade is documented as a stretch goal, not required to run.

## Run the tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -q
```

## Project structure

```
college-helpdesk-chatbot/
├── app/
│   ├── main.py       # FastAPI app + endpoints
│   ├── rag.py        # TF-IDF retrieval over app/kb/*.md
│   ├── schemas.py    # request/response models
│   └── kb/           # knowledge base (sample .md documents)
├── static/           # chat frontend (index.html, app.js, style.css)
└── tests/            # API tests
```

## License

MIT
