"""Extractive RAG over local Markdown documents.

No external API: documents in app/kb/ are split into chunks, indexed
with TF-IDF, and ranked by cosine similarity to the question. Answers
are built from the retrieved chunks and always cite their source file.
If nothing matches well enough, ask() says so instead of guessing.
"""

import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = Path(__file__).resolve().parent.parent / "kb"
MIN_SCORE = 0.10  # below this, the match is too weak to answer from


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "document"


class KnowledgeBase:
    def __init__(self, kb_dir: Path = KB_DIR) -> None:
        self.kb_dir = kb_dir
        self.chunks: list[dict] = []  # {"source", "text"}
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self.rebuild()

    def _load_chunks(self) -> list[dict]:
        chunks = []
        for path in sorted(self.kb_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = next(
                (ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("#")),
                path.stem,
            )
            for para in text.split("\n\n"):
                para = para.strip()
                if len(para) < 20 or para.startswith("#"):
                    continue
                chunks.append({"source": path.name, "text": f"{title}\n{para}"})
        return chunks

    def rebuild(self) -> None:
        self.chunks = self._load_chunks()
        if self.chunks:
            self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self._matrix = self._vectorizer.fit_transform([c["text"] for c in self.chunks])
        else:
            self._vectorizer = None
            self._matrix = None

    def doc_list(self) -> list[dict]:
        counts: dict[str, int] = {}
        for chunk in self.chunks:
            counts[chunk["source"]] = counts.get(chunk["source"], 0) + 1
        return [{"source": src, "chunks": n} for src, n in sorted(counts.items())]

    def add_document(self, title: str, content: str) -> str:
        filename = f"{_slugify(title)}.md"
        (self.kb_dir / filename).write_text(f"# {title.strip()}\n\n{content.strip()}\n")
        self.rebuild()
        return filename

    def ask(self, question: str, top_k: int = 3) -> tuple[str, list[dict]]:
        if not self.chunks or self._vectorizer is None or self._matrix is None:
            return "The knowledge base is empty. Add documents first.", []
        sims = cosine_similarity(
            self._vectorizer.transform([question]), self._matrix
        )[0]
        ranked = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)
        hits = [
            {"source": self.chunks[i]["source"], "text": self.chunks[i]["text"], "score": float(sims[i])}
            for i in ranked[:top_k]
            if sims[i] >= MIN_SCORE
        ]
        if not hits:
            return (
                "I couldn't find this in the college documents. "
                "Try rephrasing, or ask the helpdesk office directly.",
                [],
            )
        body = "\n\n".join(f"[{h['source']}] {h['text']}" for h in hits)
        answer = f"Based on the college documents:\n\n{body}"
        sources = [{"source": h["source"], "score": round(h["score"], 3)} for h in hits]
        return answer, sources
